"""
Module centralisé pour la normalisation et le fuzzy matching des textes
"""

import re
import pandas as pd
from unidecode import unidecode
from rapidfuzz import fuzz
from config.constants import CONFIG_PARAMS

# Constantes
SIMILARITY_THRESHOLD = CONFIG_PARAMS["thresholds"]["similarity"]

# Mots à ignorer lors de la normalisation
STOP_WORDS = {
    'de', 'le', 'la', 'les', 'du', 'des', 'un', 'une', 'et', 'ou', 'a', 'au', 'aux',
    'en', 'sur', 'pour', 'dans', 'par', 'avec', 'sans', 'sous'
}

# Abréviations courantes à normaliser
ABBREVIATIONS = {
    'resp': 'responsable',
    'dir': 'directeur',
    'adj': 'adjoint',
    'asst': 'assistant',
    'admin': 'administrateur',
    'dev': 'developpeur',
    'ing': 'ingenieur',
    'tech': 'technicien',
    'compta': 'comptable',
    'rh': 'ressources humaines',
    'si': 'systemes information',
    'it': 'informatique'
}

# Mots-clés métier significatifs
ROLE_KEYWORDS = {
    'chef', 'responsable', 'directeur', 'manager', 'coordinateur', 'pilote',
    'developpeur', 'analyste', 'ingenieur', 'technicien', 'architecte',
    'assistant', 'secretaire', 'gestionnaire', 'administrateur',
    'comptable', 'auditeur', 'controleur', 'consultant',
    'commercial', 'vendeur', 'acheteur', 'approvisionneur'
}

def normalize_text(text, remove_stop_words=True):
    """
    Normaliser un texte pour la comparaison

    Args:
        text: Texte à normaliser
        remove_stop_words: Si True, supprime les mots non significatifs

    Returns:
        str: Texte normalisé
    """
    if pd.isnull(text):
        return ""

    # Convertir en string et retirer les accents
    text = unidecode(str(text))

    # Convertir en minuscules
    text = text.lower()

    # Retirer les caractères non alphanumériques (garder espaces)
    text = re.sub(r'[^a-z0-9\s]', ' ', text)

    # Remplacer les espaces multiples par un seul espace
    text = re.sub(r'\s+', ' ', text).strip()

    # Remplacer les abréviations
    for abbr, full in ABBREVIATIONS.items():
        text = re.sub(r'\b' + abbr + r'\b', full, text)

    # Supprimer les mots non significatifs si demandé
    if remove_stop_words:
        words = text.split()
        filtered_words = [w for w in words if w not in STOP_WORDS]
        text = " ".join(filtered_words)

    return text

def normalize_column_name(name):
    """
    Normaliser un nom de colonne

    Args:
        name: Nom de colonne à normaliser

    Returns:
        str: Nom de colonne normalisé
    """
    name = unidecode(str(name))
    name = name.lower().replace(" ", "_")
    name = re.sub(r'[^a-z0-9_]', '', name)
    return name

def extract_key_concepts(text):
    """
    Extraire les concepts métier clés d'un texte

    Args:
        text: Texte à analyser

    Returns:
        set: Ensemble des concepts clés trouvés
    """
    if pd.isnull(text):
        return set()

    normalized = normalize_text(text)
    words = set(normalized.split())

    # Extraire les mots-clés métier
    key_concepts = words.intersection(ROLE_KEYWORDS)

    # Si pas de mots-clés trouvés, prendre les mots principaux
    if not key_concepts and words:
        # Filtrer les mots très courts
        key_concepts = {w for w in words if len(w) > 3}

    return key_concepts

def is_semantic_change(text1, text2):
    """
    Détecter si deux textes représentent un changement sémantique significatif

    Args:
        text1: Premier texte
        text2: Deuxième texte

    Returns:
        bool: True si changement sémantique significatif
    """
    concepts1 = extract_key_concepts(text1)
    concepts2 = extract_key_concepts(text2)

    # Si les ensembles de concepts sont différents, c'est un changement significatif
    if concepts1 and concepts2:
        # Calculer le taux de chevauchement
        intersection = concepts1.intersection(concepts2)
        union = concepts1.union(concepts2)

        if union:
            overlap_ratio = len(intersection) / len(union)
            # Si moins de 50% de chevauchement, c'est un changement significatif
            return overlap_ratio < 0.5

    return False

def is_similar(a, b, threshold=SIMILARITY_THRESHOLD):
    """
    Vérifier si deux chaînes sont similaires en tenant compte de la sémantique

    Args:
        a: Première chaîne
        b: Deuxième chaîne
        threshold: Seuil de similarité (0-100)

    Returns:
        bool: True si les chaînes sont similaires
    """
    if pd.isnull(a) or pd.isnull(b):
        return False

    # Normaliser pour la comparaison
    a_normalized = normalize_text(a)
    b_normalized = normalize_text(b)

    # Si identiques après normalisation, c'est similaire
    if a_normalized == b_normalized:
        return True

    # Calculer le score de similarité sur les versions normalisées
    similarity_score = fuzz.ratio(a_normalized, b_normalized)

    # Si le score est très élevé (>95), considérer comme similaire
    if similarity_score >= 95:
        return True

    # Si le score est dans la zone grise (threshold-95), vérifier la sémantique
    if similarity_score >= threshold:
        # Vérifier s'il y a un changement sémantique significatif
        if is_semantic_change(a, b):
            return False  # Changement de poste réel
        return True  # Simple variation de libellé

    return False

def get_similarity_score(a, b):
    """
    Obtenir le score de similarité entre deux chaînes

    Args:
        a: Première chaîne
        b: Deuxième chaîne

    Returns:
        float: Score de similarité (0-100)
    """
    if pd.isnull(a) or pd.isnull(b):
        return 0.0

    a_normalized = normalize_text(a)
    b_normalized = normalize_text(b)

    return fuzz.ratio(a_normalized, b_normalized)