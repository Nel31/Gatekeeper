"""
Stockage sécurisé des utilisateurs avec chiffrement
"""

import json
import os
from typing import Dict, Optional, List
from datetime import datetime
from security.encryption import encryption_manager
from security.auth.auth_manager import AuthManager
from resource_path import persistent_data_path


class UserStore:
    """Gestionnaire de stockage des utilisateurs avec chiffrement"""
    
    def __init__(self):
        self.users_file = persistent_data_path("users.enc")
        self.auth_manager = AuthManager()
        self._users_cache: Optional[Dict] = None
    
    def _load_users(self) -> Dict:
        """
        Charger les utilisateurs depuis le fichier chiffré
        
        Returns:
            Dictionnaire des utilisateurs
        """
        if not encryption_manager.is_initialized():
            return self._load_default_users()
        
        if not os.path.exists(self.users_file):
            return self._create_default_users()
        
        try:
            with open(self.users_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_content = encryption_manager.decrypt_csv_data(encrypted_data)
            users_data = json.loads(decrypted_content)
            
            # Convertir les salt de hex vers bytes
            for user_info in users_data.values():
                if 'salt' in user_info:
                    user_info['salt'] = bytes.fromhex(user_info['salt'])
            
            self._users_cache = users_data
            return users_data
            
        except Exception as e:
            print(f"⚠️ Erreur lors du chargement des utilisateurs: {e}")
            return self._create_default_users()
    
    def _save_users(self, users_data: Dict) -> None:
        """
        Sauvegarder les utilisateurs dans le fichier chiffré
        
        Args:
            users_data: Dictionnaire des utilisateurs
        """
        if not encryption_manager.is_initialized():
            return
        
        try:
            # Convertir les salt bytes vers hex pour sérialisation JSON
            serializable_data = {}
            for username, user_info in users_data.items():
                serializable_info = user_info.copy()
                if 'salt' in serializable_info and isinstance(serializable_info['salt'], bytes):
                    serializable_info['salt'] = serializable_info['salt'].hex()
                serializable_data[username] = serializable_info
            
            json_content = json.dumps(serializable_data, indent=2)
            encrypted_data = encryption_manager.encrypt_csv_data(json_content)
            
            with open(self.users_file, 'wb') as f:
                f.write(encrypted_data)
            
            self._users_cache = users_data
            
        except Exception as e:
            print(f"⚠️ Erreur lors de la sauvegarde des utilisateurs: {e}")
    
    def _load_default_users(self) -> Dict:
        """Charger les utilisateurs par défaut (fallback)"""
        return self._create_default_users()
    
    def _create_default_users(self) -> Dict:
        """
        Créer les utilisateurs par défaut
        
        Returns:
            Dictionnaire avec l'utilisateur admin par défaut
        """
        # Utilisateur admin par défaut avec mot de passe "admin123"
        admin_password = "admin123"
        admin_hash, admin_salt = self.auth_manager.hash_password(admin_password)
        
        users_data = {
            "admin": {
                "password_hash": admin_hash,
                "salt": admin_salt,
                "role": "admin",
                "created_at": datetime.now().isoformat(),
                "last_login": None,
                "is_active": True
            }
        }
        
        self._save_users(users_data)
        return users_data
    
    def verify_user(self, username: str, password: str) -> bool:
        """
        Vérifier les credentials d'un utilisateur
        
        Args:
            username: Nom d'utilisateur
            password: Mot de passe
            
        Returns:
            True si les credentials sont valides
        """
        users = self._load_users()
        
        if username not in users:
            return False
        
        user_info = users[username]
        
        # Vérifier si le compte est actif
        if not user_info.get('is_active', True):
            return False
        
        # Vérifier le mot de passe
        stored_hash = user_info['password_hash']
        salt = user_info['salt']
        
        if self.auth_manager.verify_password(password, stored_hash, salt):
            # Mettre à jour last_login
            user_info['last_login'] = datetime.now().isoformat()
            self._save_users(users)
            return True
        
        return False
    
    def create_user(self, username: str, password: str, role: str = "user") -> bool:
        """
        Créer un nouveau utilisateur
        
        Args:
            username: Nom d'utilisateur
            password: Mot de passe
            role: Rôle de l'utilisateur
            
        Returns:
            True si l'utilisateur a été créé
        """
        users = self._load_users()
        
        if username in users:
            return False  # Utilisateur déjà existant
        
        password_hash, salt = self.auth_manager.hash_password(password)
        
        users[username] = {
            "password_hash": password_hash,
            "salt": salt,
            "role": role,
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "is_active": True
        }
        
        self._save_users(users)
        return True
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """
        Changer le mot de passe d'un utilisateur
        
        Args:
            username: Nom d'utilisateur
            old_password: Ancien mot de passe
            new_password: Nouveau mot de passe
            
        Returns:
            True si le changement a réussi
        """
        if not self.verify_user(username, old_password):
            return False
        
        users = self._load_users()
        
        new_hash, new_salt = self.auth_manager.hash_password(new_password)
        
        users[username]['password_hash'] = new_hash
        users[username]['salt'] = new_salt
        
        self._save_users(users)
        return True
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """
        Récupérer les informations d'un utilisateur
        
        Args:
            username: Nom d'utilisateur
            
        Returns:
            Informations utilisateur (sans le hash du mot de passe)
        """
        users = self._load_users()
        
        if username not in users:
            return None
        
        user_info = users[username].copy()
        # Supprimer les informations sensibles
        user_info.pop('password_hash', None)
        user_info.pop('salt', None)
        
        return user_info
    
    def list_users(self) -> List[str]:
        """
        Lister tous les utilisateurs
        
        Returns:
            Liste des noms d'utilisateurs
        """
        users = self._load_users()
        return list(users.keys())
    
    def deactivate_user(self, username: str) -> bool:
        """
        Désactiver un utilisateur
        
        Args:
            username: Nom d'utilisateur
            
        Returns:
            True si la désactivation a réussi
        """
        users = self._load_users()
        
        if username not in users:
            return False
        
        users[username]['is_active'] = False
        self._save_users(users)
        return True


# Instance globale
user_store = UserStore()
