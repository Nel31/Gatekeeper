"""
Exceptions spécifiques au module de sécurité
"""

class EncryptionError(Exception):
    """Erreur générale de chiffrement"""
    pass

class DecryptionError(EncryptionError):
    """Erreur de déchiffrement"""
    pass

class KeyDerivationError(EncryptionError):
    """Erreur de dérivation de clé"""
    pass 