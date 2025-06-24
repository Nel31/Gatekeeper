"""
Utilitaire pour gérer les chemins de ressources dans l'application empaquetée
À ajouter dans votre projet pour gérer correctement les fichiers de données
"""

import os
import sys


def resource_path(relative_path):
    """
    Obtenir le chemin absolu vers une ressource, fonctionne pour dev et PyInstaller

    Args:
        relative_path: Chemin relatif vers la ressource

    Returns:
        str: Chemin absolu vers la ressource
    """
    try:
        # PyInstaller crée un dossier temp et stocke le chemin dans _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # En développement, utiliser le répertoire courant
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def data_path(filename):
    """
    Obtenir le chemin vers un fichier de données

    Args:
        filename: Nom du fichier dans le dossier data/

    Returns:
        str: Chemin complet vers le fichier
    """
    return resource_path(os.path.join('data', filename))


def config_path(filename):
    """
    Obtenir le chemin vers un fichier de configuration

    Args:
        filename: Nom du fichier dans le dossier config/

    Returns:
        str: Chemin complet vers le fichier
    """
    return resource_path(os.path.join('config', filename))


def get_persistent_data_path():
    """
    Obtenir le chemin pour les données persistantes (Windows)
    
    Returns:
        str: Chemin vers le dossier de données persistantes
    """
    appdata = os.environ.get('APPDATA')
    if appdata:
        data_dir = os.path.join(appdata, 'Gatekeeper', 'data')
    else:
        # Fallback si APPDATA n'est pas défini
        data_dir = os.path.join(os.path.expanduser('~'), 'Gatekeeper', 'data')
    
    # Créer le dossier s'il n'existe pas
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def persistent_data_path(filename):
    """
    Obtenir le chemin complet vers un fichier de données persistantes
    
    Args:
        filename: Nom du fichier
        
    Returns:
        str: Chemin complet vers le fichier
    """
    return os.path.join(get_persistent_data_path(), filename)

# Exemple d'utilisation dans vos modules:
#
# from resource_path import data_path
#
# # Au lieu de:
# CSV_VARIATIONS_DIR = "data/variations_directions.csv"
#
# # Utiliser:
# CSV_VARIATIONS_DIR = data_path("variations_directions.csv")