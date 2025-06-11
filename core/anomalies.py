import pandas as pd
import numpy as np
from rapidfuzz.fuzz import ratio
from mapping.profils_valides import charger_profils_valides, est_changement_profil_valide, ajouter_profil_valide
from mapping.directions_conservees import charger_directions_conservees, est_direction_conservee, ajouter_direction_conservee

SIMILARITY_THRESHOLD = 85
SEUIL_INACTIVITE = 120

def is_similar(a, b, threshold=SIMILARITY_THRESHOLD):
    if pd.isnull(a) or pd.isnull(b):
        return False
    return ratio(str(a), str(b)) >= threshold

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