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

# Exemple d'utilisation dans vos modules:
#
# from resource_path import data_path
#
# # Au lieu de:
# CSV_VARIATIONS_DIR = "data/variations_directions.csv"
#
# # Utiliser:
# CSV_VARIATIONS_DIR = data_path("variations_directions.csv")