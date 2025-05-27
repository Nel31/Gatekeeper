import pandas as pd
from datetime import datetime
import os

CSV_WHITELIST = "profils_valides.csv"

def charger_profils_valides(path=CSV_WHITELIST):
    if not os.path.exists(path):
        return pd.DataFrame(columns=["profil_extraction", "profil_rh", "date_validation", "certificateur"])
    return pd.read_csv(path)

def est_changement_profil_valide(row, profils_valides):
    f = (
        (profils_valides['profil_extraction'] == row['profil']) &
        (profils_valides['profil_rh'] == row['profil_rh'])
    )
    return profils_valides[f].shape[0] > 0

def ajouter_profil_valide(row, certificateur, path=CSV_WHITELIST):
    profils_valides = charger_profils_valides(path)
    nv = {
        "profil_extraction": row['profil'],
        "profil_rh": row['profil_rh'],
        "date_validation": datetime.now().strftime('%Y-%m-%d'),
        "certificateur": certificateur
    }
    profils_valides = pd.concat([profils_valides, pd.DataFrame([nv])], ignore_index=True)
    profils_valides.drop_duplicates(inplace=True)
    profils_valides.to_csv(path, index=False)
