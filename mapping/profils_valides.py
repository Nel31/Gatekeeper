import pandas as pd
from datetime import datetime
import os
from core.text_utils import is_semantic_change

from resource_path import data_path

CSV_VARIATIONS = data_path("variations_profils.csv")
CSV_CHANGEMENTS = data_path("changements_profils.csv")
CSV_WHITELIST = data_path("profils_valides.csv")

def charger_variations_profils(path=CSV_VARIATIONS):
    """Charger les variations d'écriture connues"""
    if not os.path.exists(path):
        return pd.DataFrame(columns=["profil_extraction", "profil_rh", "date_validation", "certificateur", "type_variation"])
    return pd.read_csv(path)

def charger_changements_profils(path=CSV_CHANGEMENTS):
    """Charger les changements réels validés"""
    if not os.path.exists(path):
        return pd.DataFrame(columns=["profil_extraction", "profil_rh", "date_validation", "certificateur", "type_changement"])
    return pd.read_csv(path)

def charger_profils_valides(path=CSV_WHITELIST):
    """Charger tous les profils validés (compatibilité)"""
    variations = charger_variations_profils()
    changements = charger_changements_profils()
    
    # Fusionner pour compatibilité
    all_profils = pd.concat([
        variations[['profil_extraction', 'profil_rh', 'date_validation', 'certificateur']],
        changements[['profil_extraction', 'profil_rh', 'date_validation', 'certificateur']]
    ], ignore_index=True)
    
    return all_profils

def classifier_changement_profil(profil_ext, profil_rh):
    """
    Classifier un changement de profil
    
    Returns:
        tuple: (type, est_connu) où type est 'variation', 'changement' ou None
    """
    # Vérifier si c'est une variation connue
    variations = charger_variations_profils()
    if len(variations[(variations['profil_extraction'] == profil_ext) & 
                     (variations['profil_rh'] == profil_rh)]) > 0:
        return ('variation', True)
    
    # Vérifier si c'est un changement connu
    changements = charger_changements_profils()
    if len(changements[(changements['profil_extraction'] == profil_ext) & 
                      (changements['profil_rh'] == profil_rh)]) > 0:
        return ('changement', True)
    
    # Analyser sémantiquement
    if is_semantic_change(profil_ext, profil_rh):
        return ('changement', False)
    else:
        return ('variation', False)

def ajouter_profil_valide(row, certificateur, path=CSV_WHITELIST):
    """Ajouter un profil validé en distinguant le type"""
    profil_ext = row.get('profil', '')
    profil_rh = row.get('profil_rh', '')
    
    type_change, _ = classifier_changement_profil(profil_ext, profil_rh)
    
    if type_change == 'variation':
        ajouter_variation_profil(row, certificateur)
    else:
        ajouter_changement_profil(row, certificateur)

def ajouter_variation_profil(row, certificateur, path=CSV_VARIATIONS):
    """Ajouter une variation d'écriture"""
    variations = charger_variations_profils(path)
    nv = {
        "profil_extraction": row['profil'],
        "profil_rh": row['profil_rh'],
        "date_validation": datetime.now().strftime('%Y-%m-%d'),
        "certificateur": certificateur,
        "type_variation": "ecriture"
    }
    variations = pd.concat([variations, pd.DataFrame([nv])], ignore_index=True)
    variations.drop_duplicates(subset=['profil_extraction', 'profil_rh'], inplace=True)
    variations.to_csv(path, index=False)

def ajouter_changement_profil(row, certificateur, type_changement="evolution", path=CSV_CHANGEMENTS):
    """Ajouter un changement réel"""
    changements = charger_changements_profils(path)
    nv = {
        "profil_extraction": row['profil'],
        "profil_rh": row['profil_rh'],
        "date_validation": datetime.now().strftime('%Y-%m-%d'),
        "certificateur": certificateur,
        "type_changement": type_changement
    }
    changements = pd.concat([changements, pd.DataFrame([nv])], ignore_index=True)
    changements.drop_duplicates(subset=['profil_extraction', 'profil_rh'], inplace=True)
    changements.to_csv(path, index=False)

def est_changement_profil_valide(row, profils_valides=None):
    """Vérifier si un changement est déjà validé"""
    if profils_valides is None:
        profils_valides = charger_profils_valides()
    
    f = (
        (profils_valides['profil_extraction'] == row['profil']) &
        (profils_valides['profil_rh'] == row['profil_rh'])
    )
    return profils_valides[f].shape[0] > 0
