import pandas as pd
from rapidfuzz.fuzz import ratio
from profils_valides import charger_profils_valides, est_changement_profil_valide, ajouter_profil_valide
from directions_conservees import charger_directions_conservees, est_direction_conservee, ajouter_direction_conservee

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
    for i, row in df.iterrows():
        tags = []
        decision = ""
        compte_non_rh = row.get('compte_non_rh', False)
        profil, profil_rh = row.get('profil', ""), row.get('profil_rh', "")
        direction, direction_rh = row.get('direction', ""), row.get('direction_rh', "")
        inactif = (row.get('days_inactive') is not None) and (row['days_inactive'] is not None) and (row['days_inactive'] > SEUIL_INACTIVITE)
        # 1. Compte non RH
        if compte_non_rh:
            tags.append("Compte non RH")

        # 2. Changement de direction à vérifier (fuzzy, whitelist globale)
        if not compte_non_rh and not is_similar(direction, direction_rh):
            if is_similar(direction, direction_rh):  # rapidfuzz valide (rare car déjà testé)
                ajouter_direction_conservee(row, certificateur)
            elif est_direction_conservee(row, directions_conservees):
                pass  # whitelist direction, rien à faire
            else:
                tags.append("Changement de direction à vérifier")
        elif not compte_non_rh and is_similar(direction, direction_rh):
            if not est_direction_conservee(row, directions_conservees):
                ajouter_direction_conservee(row, certificateur)

        # 3. Changement de profil à vérifier (fuzzy, whitelist globale)
        if not compte_non_rh and not is_similar(profil, profil_rh):
            if is_similar(profil, profil_rh):
                ajouter_profil_valide(row, certificateur)
            elif est_changement_profil_valide(row, profils_valides):
                pass
            else:
                tags.append("Changement de profil à vérifier")
        elif not compte_non_rh and is_similar(profil, profil_rh):
            if not est_changement_profil_valide(row, profils_valides):
                ajouter_profil_valide(row, certificateur)

        # 4. Inactivité
        if inactif:
            tags.append("Compte potentiellement inactif")
            decision = "Désactiver"
        anomalies.append(", ".join(tags))
        decisions.append(decision if decision else "")
    df['anomalie'] = anomalies
    if 'decision_manuelle' not in df.columns:
        df['decision_manuelle'] = ""
    for i, d in enumerate(decisions):
        if d:
            df.at[df.index[i], 'decision_manuelle'] = d
    return df

def extraire_cas_a_verifier(df):
    return df[(df['anomalie'].str.len() > 0) & (df['decision_manuelle'] == "")]
