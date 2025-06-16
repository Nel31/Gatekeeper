import pandas as pd
import numpy as np
import re
from unidecode import unidecode
from rapidfuzz.fuzz import ratio
from mapping.profils_valides import charger_profils_valides, est_changement_profil_valide, ajouter_profil_valide
from mapping.directions_conservees import charger_directions_conservees, est_direction_conservee, ajouter_direction_conservee

SIMILARITY_THRESHOLD = 85
SEUIL_INACTIVITE = 120

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

# Mots-clés métier significatifs pour détecter les changements de poste
ROLE_KEYWORDS = {
    'chef', 'responsable', 'directeur', 'manager', 'coordinateur', 'pilote',
    'developpeur', 'analyste', 'ingenieur', 'technicien', 'architecte',
    'assistant', 'secretaire', 'gestionnaire', 'administrateur',
    'comptable', 'auditeur', 'controleur', 'consultant',
    'commercial', 'vendeur', 'acheteur', 'approvisionneur'
}

def normalize_for_comparison(text):
    """Normaliser le texte pour la comparaison"""
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
    
    # Supprimer les mots non significatifs
    words = text.split()
    filtered_words = [w for w in words if w not in STOP_WORDS]
    
    return " ".join(filtered_words)

def extract_key_concepts(text):
    """Extraire les concepts métier clés d'un texte"""
    if pd.isnull(text):
        return set()
    
    normalized = normalize_for_comparison(text)
    words = set(normalized.split())
    
    # Extraire les mots-clés métier
    key_concepts = words.intersection(ROLE_KEYWORDS)
    
    # Si pas de mots-clés trouvés, prendre les mots principaux
    if not key_concepts and words:
        # Filtrer les mots très courts
        key_concepts = {w for w in words if len(w) > 3}
    
    return key_concepts

def is_semantic_change(text1, text2):
    """Détecter si deux textes représentent un changement sémantique significatif"""
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
    """Vérifier si deux chaînes sont similaires en tenant compte de la sémantique"""
    if pd.isnull(a) or pd.isnull(b):
        return False
    
    # Normaliser pour la comparaison
    a_normalized = normalize_for_comparison(a)
    b_normalized = normalize_for_comparison(b)
    
    # Si identiques après normalisation, c'est similaire
    if a_normalized == b_normalized:
        return True
    
    # Calculer le score de similarité sur les versions normalisées
    similarity_score = ratio(a_normalized, b_normalized)
    
    # Si le score est très élevé (>95), considérer comme similaire
    if similarity_score >= 95:
        return True
    
    # Si le score est dans la zone grise (85-95), vérifier la sémantique
    if similarity_score >= threshold:
        # Vérifier s'il y a un changement sémantique significatif
        if is_semantic_change(a, b):
            return False  # Changement de poste réel
        return True  # Simple variation de libellé
    
    return False

def detecter_anomalies(df, certificateur):
    profils_valides = charger_profils_valides()
    directions_conservees = charger_directions_conservees()
    df['days_inactive'] = (df['extraction_date'] - df['last_login']).dt.days
    
    anomalies = []
    decisions = []
    cas_auto = []  # Nouveau : marquer les cas automatiques
    
    for i, row in df.iterrows():
        tags = []
        decision = ""
        is_auto = False  # Flag pour cas automatique
        
        compte_non_rh = row.get('compte_non_rh', False)
        profil, profil_rh = row.get('profil', ""), row.get('profil_rh', "")
        direction, direction_rh = row.get('direction', ""), row.get('direction_rh', "")
        inactif = (row.get('days_inactive') is not None) and (row['days_inactive'] is not None) and (row['days_inactive'] > SEUIL_INACTIVITE)
        
        # 1. Compte non RH
        if compte_non_rh:
            tags.append("Compte non RH")

        # 2. Changement de direction à vérifier
        if not compte_non_rh and not is_similar(direction, direction_rh):
            if est_direction_conservee(row, directions_conservees):
                # Cas automatique : direction whitelistée
                is_auto = True
                decision = "Conserver"
            else:
                tags.append("Changement de direction à vérifier")
        elif not compte_non_rh and is_similar(direction, direction_rh):
            # Fuzzy match validé automatiquement
            if not est_direction_conservee(row, directions_conservees):
                ajouter_direction_conservee(row, certificateur)

        # 3. Changement de profil à vérifier
        if not compte_non_rh and not is_similar(profil, profil_rh):
            if est_changement_profil_valide(row, profils_valides):
                # Cas automatique : profil whitelisté
                is_auto = True
                decision = "Conserver"
            else:
                tags.append("Changement de profil à vérifier")
        elif not compte_non_rh and is_similar(profil, profil_rh):
            # Fuzzy match validé automatiquement
            if not est_changement_profil_valide(row, profils_valides):
                ajouter_profil_valide(row, certificateur)

        # 4. Inactivité - TOUJOURS automatique
        if inactif:
            tags.append("Compte potentiellement inactif")
            decision = "Désactiver"
            is_auto = True  # Les inactifs sont TOUJOURS automatiques
        
        anomalies.append(", ".join(tags))
        decisions.append(decision)
        cas_auto.append(is_auto)
    
    df['anomalie'] = anomalies
    df['cas_automatique'] = cas_auto  # Nouveau champ
    
    if 'decision_manuelle' not in df.columns:
        df['decision_manuelle'] = ""
    
    # Remplir automatiquement les décisions pour les cas automatiques
    for i, (d, auto) in enumerate(zip(decisions, cas_auto)):
        if d and auto:
            df.at[df.index[i], 'decision_manuelle'] = d
    
    return df

def extraire_cas_a_verifier(df):
    """Extraire uniquement les cas nécessitant une vérification manuelle"""
    # Cas à vérifier = anomalie présente ET pas de décision ET pas automatique
    return df[
        (df['anomalie'].str.len() > 0) & 
        (df['decision_manuelle'] == "") & 
        (~df.get('cas_automatique', False))
    ]

def extraire_cas_automatiques(df):
    """Extraire les cas traités automatiquement"""
    return df[
        (df['anomalie'].str.len() > 0) & 
        (df.get('cas_automatique', False) == True)
    ]

def compter_anomalies_par_type(df):
    """Compter les anomalies par type pour les statistiques"""
    anomalies_count = {}
    for anomalie in df['anomalie']:
        if anomalie:
            for a in anomalie.split(', '):
                if a:
                    anomalies_count[a] = anomalies_count.get(a, 0) + 1
    return anomalies_count