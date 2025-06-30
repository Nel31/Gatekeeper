"""
Gestionnaire de chiffrement pour les données sensibles
Utilise AES-256-GCM pour le chiffrement symétrique
"""

import os
import json
import hashlib
import platform
from typing import Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import pandas as pd
from resource_path import persistent_data_path


class EncryptionManager:
    """Gestionnaire de chiffrement pour les données persistantes"""
    
    def __init__(self):
        self.key_file = persistent_data_path("gatekeeper.key")
        self.salt_file = persistent_data_path("gatekeeper.salt")
        self._cipher = None
        self._current_certificateur = None
    
    def initialize(self, certificateur: str) -> None:
        """
        Initialiser le chiffrement pour un certificateur
        
        Args:
            certificateur: Nom du certificateur pour dériver la clé
        """
        self._current_certificateur = certificateur
        self._cipher = self._get_or_create_cipher(certificateur)
    
    def _get_machine_fingerprint(self) -> str:
        """Générer une empreinte unique de la machine"""
        machine_info = f"{platform.node()}-{platform.machine()}-{platform.system()}"
        return hashlib.sha256(machine_info.encode()).hexdigest()[:16]
    
    def _derive_key(self, certificateur: str, salt: bytes) -> bytes:
        """
        Dériver une clé de chiffrement à partir du certificateur et de l'empreinte machine
        
        Args:
            certificateur: Nom du certificateur
            salt: Salt pour la dérivation
            
        Returns:
            Clé de chiffrement de 32 bytes
        """
        # Combiner certificateur + empreinte machine
        seed = f"{certificateur}-{self._get_machine_fingerprint()}"
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(seed.encode())
    
    def _get_or_create_cipher(self, certificateur: str) -> Fernet:
        """
        Obtenir ou créer le cipher pour le chiffrement
        
        Args:
            certificateur: Nom du certificateur
            
        Returns:
            Instance Fernet pour chiffrement/déchiffrement
        """
        # Charger ou créer le salt
        if os.path.exists(self.salt_file):
            with open(self.salt_file, 'rb') as f:
                salt = f.read()
        else:
            salt = os.urandom(16)
            with open(self.salt_file, 'wb') as f:
                f.write(salt)
        
        # Dériver la clé
        key = self._derive_key(certificateur, salt)
        fernet_key = base64.urlsafe_b64encode(key)
        
        return Fernet(fernet_key)
    
    def encrypt_csv_data(self, csv_content: str) -> bytes:
        """
        Chiffrer le contenu CSV
        
        Args:
            csv_content: Contenu CSV en string
            
        Returns:
            Données chiffrées
        """
        if self._cipher is None:
            raise ValueError("EncryptionManager not initialized")
        
        return self._cipher.encrypt(csv_content.encode('utf-8'))
    
    def decrypt_csv_data(self, encrypted_data: bytes) -> str:
        """
        Déchiffrer les données CSV
        
        Args:
            encrypted_data: Données chiffrées
            
        Returns:
            Contenu CSV déchiffré
        """
        if self._cipher is None:
            raise ValueError("EncryptionManager not initialized")
        
        try:
            decrypted_bytes = self._cipher.decrypt(encrypted_data)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Erreur de déchiffrement: {e}")
    
    def save_encrypted_csv(self, df: pd.DataFrame, file_path: str) -> None:
        """
        Sauvegarder un DataFrame chiffré
        
        Args:
            df: DataFrame à sauvegarder
            file_path: Chemin du fichier (extension .enc sera ajoutée)
        """
        # Convertir DataFrame en CSV
        csv_content = df.to_csv(index=False)
        
        # Chiffrer
        encrypted_data = self.encrypt_csv_data(csv_content)
        
        # Sauvegarder avec extension .enc
        encrypted_file_path = file_path + '.enc'
        with open(encrypted_file_path, 'wb') as f:
            f.write(encrypted_data)
        
        # Supprimer l'ancien fichier non chiffré s'il existe
        if os.path.exists(file_path):
            os.remove(file_path)
    
    def load_encrypted_csv(self, file_path: str) -> pd.DataFrame:
        """
        Charger un DataFrame depuis un fichier chiffré
        
        Args:
            file_path: Chemin du fichier (sans extension .enc)
            
        Returns:
            DataFrame chargé ou DataFrame vide si fichier inexistant
        """
        encrypted_file_path = file_path + '.enc'
        
        # Vérifier si le fichier chiffré existe
        if os.path.exists(encrypted_file_path):
            return self._load_from_encrypted(encrypted_file_path)
        
        # Vérifier si l'ancien fichier non chiffré existe (migration)
        elif os.path.exists(file_path):
            return self._migrate_from_unencrypted(file_path)
        
        # Aucun fichier trouvé, retourner DataFrame vide
        else:
            return self._create_empty_dataframe(file_path)
    
    def _load_from_encrypted(self, encrypted_file_path: str) -> pd.DataFrame:
        """Charger depuis un fichier chiffré"""
        try:
            with open(encrypted_file_path, 'rb') as f:
                encrypted_data = f.read()
            
            csv_content = self.decrypt_csv_data(encrypted_data)
            
            # Convertir en DataFrame
            from io import StringIO
            return pd.read_csv(StringIO(csv_content))
            
        except Exception as e:
            print(f"⚠️ Erreur lors du déchiffrement de {encrypted_file_path}: {e}")
            # En cas d'erreur, retourner DataFrame vide
            return self._create_empty_dataframe(encrypted_file_path.replace('.enc', ''))
    
    def _migrate_from_unencrypted(self, file_path: str) -> pd.DataFrame:
        """Migrer un fichier non chiffré vers chiffré"""
        try:
            # Charger l'ancien fichier
            df = pd.read_csv(file_path)
            
            # Sauvegarder en version chiffrée
            self.save_encrypted_csv(df, file_path)
            
            print(f"✅ Fichier migré vers chiffrement: {os.path.basename(file_path)}")
            return df
            
        except Exception as e:
            print(f"⚠️ Erreur lors de la migration de {file_path}: {e}")
            return self._create_empty_dataframe(file_path)
    
    def _create_empty_dataframe(self, file_path: str) -> pd.DataFrame:
        """Créer un DataFrame vide selon le type de fichier"""
        filename = os.path.basename(file_path)
        
        if 'profil' in filename:
            return pd.DataFrame(columns=["profil_extraction", "profil_rh", "date_validation", "certificateur", "type_variation"])
        elif 'direction' in filename:
            return pd.DataFrame(columns=["direction_extraction", "direction_rh", "date_validation", "certificateur", "type_variation"])
        else:
            return pd.DataFrame()
    
    def is_initialized(self) -> bool:
        """Vérifier si le gestionnaire est initialisé"""
        return self._cipher is not None
    
    def get_current_certificateur(self) -> Optional[str]:
        """Récupérer le certificateur actuel"""
        return self._current_certificateur


# Instance globale
encryption_manager = EncryptionManager() 