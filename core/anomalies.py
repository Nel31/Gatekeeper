import pandas as pd
import numpy as np
from core.text_utils import (
    is_similar, is_semantic_change, extract_key_concepts,
    normalize_text, SIMILARITY_THRESHOLD
)
from mapping.profils_valides import (
    charger_profils_valides, est_changement_profil_valide, 
    ajouter_profil_valide, classifier_changement_profil
)
from mapping.directions_conservees import (
    charger_directions_conservees, est_direction_conservee, 
    ajouter_direction_valide, classifier_changement_direction
)

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

def detecter_anomalies(df, certificateur):
    profils_valides = charger_profils_valides()
    directions_conservees = charger_directions_conservees()
    df['days_inactive'] = (df['extraction_date'] - df['last_login']).dt.days
    
    anomalies = []
    decisions = []
    cas_auto = []
    
    for i, row in df.iterrows():
        tags = []
        decision = ""
        is_auto = False
        
        compte_non_rh = row.get('compte_non_rh', False)
        profil, profil_rh = row.get('profil', ""), row.get('profil_rh', "")
        direction, direction_rh = row.get('direction', ""), row.get('direction_rh', "")
        inactif = (row.get('days_inactive') is not None) and (row['days_inactive'] > SEUIL_INACTIVITE)
        
        # --- AJOUT DES TAGS (toujours additif) ---
        if inactif:
            tags.append("Compte potentiellement inactif")
        if compte_non_rh:
            tags.append("Compte non RH")

        # --- DÉTERMINATION DE LA DÉCISION ET is_auto (logique prioritaire) ---
        if inactif:
            decision = "Désactiver"
            is_auto = True
        elif compte_non_rh:
            decision = "Désactiver"
            is_auto = True
        elif not is_similar(direction, direction_rh):
            if est_direction_conservee(row, directions_conservees):
                decision = "Conserver"
                is_auto = True
            elif is_semantic_change(direction, direction_rh):
                tags.append("Changement de direction à vérifier") # Tag ici car pas de décision auto
            else:
                # Variation d'écriture - Auto-conserver
                decision = "Conserver"
                is_auto = True
                tags.append("Direction harmonisée") # Tag ici car décision auto
                ajouter_direction_valide(row, certificateur)
        elif not is_similar(profil, profil_rh):
            if est_changement_profil_valide(row, profils_valides):
                decision = "Conserver"
                is_auto = True
            elif is_semantic_change(profil, profil_rh):
                tags.append("Changement de profil à vérifier") # Tag ici car pas de décision auto
            else:
                # Variation d'écriture - Auto-conserver
                decision = "Conserver"
                is_auto = True
                tags.append("Profil harmonisé") # Tag ici car décision auto
                ajouter_profil_valide(row, certificateur)
        
        anomalies.append(", ".join(tags))
        decisions.append(decision)
        cas_auto.append(is_auto)
    
    df['anomalie'] = anomalies
    df['cas_automatique'] = cas_auto
    
    if 'decision_manuelle' not in df.columns:
        df['decision_manuelle'] = ""
    
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