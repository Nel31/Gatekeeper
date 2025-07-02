"""
Gestionnaire d'authentification avec hachage sécurisé des mots de passe
"""

import hashlib
import secrets
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class AuthManager:
    """Gestionnaire d'authentification et de session"""
    
    def __init__(self):
        self.current_user: Optional[str] = None
        self.session_start: Optional[datetime] = None
        self.session_timeout: int = 480  # 8 heures en minutes
        self.failed_attempts: Dict[str, int] = {}
        self.lockout_duration: int = 15  # 15 minutes
        self.last_attempt: Dict[str, datetime] = {}
    
    def hash_password(self, password: str, salt: bytes = None) -> tuple[str, bytes]:
        """
        Hacher un mot de passe avec salt
        
        Args:
            password: Mot de passe en clair
            salt: Salt optionnel (généré automatiquement si non fourni)
            
        Returns:
            Tuple (hash_hex, salt)
        """
        if salt is None:
            salt = secrets.token_bytes(32)
        
        # Utiliser PBKDF2 avec SHA-256
        pwdhash = hashlib.pbkdf2_hmac('sha256', 
                                     password.encode('utf-8'), 
                                     salt, 
                                     100000)  # 100k iterations
        
        return pwdhash.hex(), salt
    
    def verify_password(self, password: str, stored_hash: str, salt: bytes) -> bool:
        """
        Vérifier un mot de passe
        
        Args:
            password: Mot de passe en clair
            stored_hash: Hash stocké
            salt: Salt utilisé
            
        Returns:
            True si le mot de passe est correct
        """
        computed_hash, _ = self.hash_password(password, salt)
        return computed_hash == stored_hash
    
    def is_account_locked(self, username: str) -> bool:
        """
        Vérifier si un compte est verrouillé
        
        Args:
            username: Nom d'utilisateur
            
        Returns:
            True si le compte est verrouillé
        """
        if username not in self.failed_attempts:
            return False
        
        if self.failed_attempts[username] < 3:
            return False
        
        last_attempt = self.last_attempt.get(username)
        if last_attempt is None:
            return False
        
        lockout_until = last_attempt + timedelta(minutes=self.lockout_duration)
        if datetime.now() > lockout_until:
            # Reset après expiration du verrouillage
            self.failed_attempts[username] = 0
            return False
        
        return True
    
    def record_failed_attempt(self, username: str) -> None:
        """
        Enregistrer une tentative de connexion échouée
        
        Args:
            username: Nom d'utilisateur
        """
        self.failed_attempts[username] = self.failed_attempts.get(username, 0) + 1
        self.last_attempt[username] = datetime.now()
    
    def reset_failed_attempts(self, username: str) -> None:
        """
        Réinitialiser les tentatives échouées après connexion réussie
        
        Args:
            username: Nom d'utilisateur
        """
        if username in self.failed_attempts:
            del self.failed_attempts[username]
        if username in self.last_attempt:
            del self.last_attempt[username]
    
    def authenticate(self, username: str, password: str, user_store) -> bool:
        """
        Authentifier un utilisateur
        
        Args:
            username: Nom d'utilisateur
            password: Mot de passe
            user_store: Instance UserStore
            
        Returns:
            True si l'authentification réussit
        """
        # Vérifier si le compte est verrouillé
        if self.is_account_locked(username):
            return False
        
        # Vérifier les credentials
        if user_store.verify_user(username, password):
            self.current_user = username
            self.session_start = datetime.now()
            self.reset_failed_attempts(username)
            return True
        else:
            self.record_failed_attempt(username)
            return False
    
    def is_authenticated(self) -> bool:
        """
        Vérifier si l'utilisateur est authentifié et la session valide
        
        Returns:
            True si authentifié et session valide
        """
        if self.current_user is None or self.session_start is None:
            return False
        
        # Vérifier le timeout de session
        session_duration = datetime.now() - self.session_start
        if session_duration.total_seconds() > (self.session_timeout * 60):
            self.logout()
            return False
        
        return True
    
    def refresh_session(self) -> None:
        """Rafraîchir la session (étendre le timeout)"""
        if self.is_authenticated():
            self.session_start = datetime.now()
    
    def logout(self) -> None:
        """Déconnecter l'utilisateur"""
        self.current_user = None
        self.session_start = None
    
    def get_current_user(self) -> Optional[str]:
        """
        Récupérer l'utilisateur actuellement connecté
        
        Returns:
            Nom d'utilisateur ou None
        """
        if self.is_authenticated():
            return self.current_user
        return None
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        Récupérer les informations de session
        
        Returns:
            Dictionnaire avec les infos de session
        """
        if not self.is_authenticated():
            return {"authenticated": False}
        
        session_duration = datetime.now() - self.session_start
        remaining_time = (self.session_timeout * 60) - session_duration.total_seconds()
        
        return {
            "authenticated": True,
            "user": self.current_user,
            "session_start": self.session_start.isoformat(),
            "remaining_minutes": max(0, remaining_time // 60)
        }


# Instance globale
auth_manager = AuthManager()
