import pandas as pd
from datetime import datetime
import os
from core.text_utils import is_semantic_change

from resource_path import data_path

CSV_VARIATIONS_DIR = data_path("variations_directions.csv")
CSV_CHANGEMENTS_DIR = data_path("changements_directions.csv")
CSV_WHITELIST_DIR = data_path("directions_conservees.csv")

def charger_variations_directions(path=CSV_VARIATIONS_DIR):
    """Charger les variations d'écriture des directions connues"""
    if not os.path.exists(path):
        return pd.DataFrame(columns=["direction_extraction", "direction_rh", "date_validation", "certificateur", "type_variation"])
    return pd.read_csv(path)

def charger_changements_directions(path=CSV_CHANGEMENTS_DIR):
    """Charger les changements réels de directions validés"""
    if not os.path.exists(path):
        return pd.DataFrame(columns=["direction_extraction", "direction_rh", "date_validation", "certificateur", "type_changement"])
    return pd.read_csv(path)

def charger_directions_conservees(path=CSV_WHITELIST_DIR):
    """Charger toutes les directions validées (compatibilité)"""
    variations = charger_variations_directions()
    changements = charger_changements_directions()
    
    # Fusionner pour compatibilité
    all_directions = pd.concat([
        variations[['direction_extraction', 'direction_rh', 'date_validation', 'certificateur']],
        changements[['direction_extraction', 'direction_rh', 'date_validation', 'certificateur']]
    ], ignore_index=True)
    
    return all_directions

def classifier_changement_direction(direction_ext, direction_rh):
    """
    Classifier un changement de direction
    
    Returns:
        tuple: (type, est_connu) où type est 'variation', 'changement' ou None
    """
    # Vérifier si c'est une variation connue
    variations = charger_variations_directions()
    if len(variations[(variations['direction_extraction'] == direction_ext) & 
                     (variations['direction_rh'] == direction_rh)]) > 0:
        return ('variation', True)
    
    # Vérifier si c'est un changement connu
    changements = charger_changements_directions()
    if len(changements[(changements['direction_extraction'] == direction_ext) & 
                      (changements['direction_rh'] == direction_rh)]) > 0:
        return ('changement', True)
    
    # Analyser sémantiquement
    if is_semantic_change(direction_ext, direction_rh):
        return ('changement', False)
    else:
        return ('variation', False)

def ajouter_direction_valide(row, certificateur, path=CSV_WHITELIST_DIR):
    """Ajouter une direction validée en distinguant le type"""
    direction_ext = row.get('direction', '')
    direction_rh = row.get('direction_rh', '')
    
    type_change, _ = classifier_changement_direction(direction_ext, direction_rh)
    
    if type_change == 'variation':
        ajouter_variation_direction(row, certificateur)
    else:
        ajouter_changement_direction(row, certificateur)

def ajouter_variation_direction(row, certificateur, path=CSV_VARIATIONS_DIR):
    """Ajouter une variation d'écriture de direction"""
    variations = charger_variations_directions(path)
    nv = {
        "direction_extraction": row['direction'],
        "direction_rh": row['direction_rh'],
        "date_validation": datetime.now().strftime('%Y-%m-%d'),
        "certificateur": certificateur,
        "type_variation": "ecriture"
    }
    variations = pd.concat([variations, pd.DataFrame([nv])], ignore_index=True)
    variations.drop_duplicates(subset=['direction_extraction', 'direction_rh'], inplace=True)
    variations.to_csv(path, index=False)

def ajouter_changement_direction(row, certificateur, type_changement="evolution", path=CSV_CHANGEMENTS_DIR):
    """Ajouter un changement réel de direction"""
    changements = charger_changements_directions(path)
    nv = {
        "direction_extraction": row['direction'],
        "direction_rh": row['direction_rh'],
        "date_validation": datetime.now().strftime('%Y-%m-%d'),
        "certificateur": certificateur,
        "type_changement": type_changement
    }
    changements = pd.concat([changements, pd.DataFrame([nv])], ignore_index=True)
    changements.drop_duplicates(subset=['direction_extraction', 'direction_rh'], inplace=True)
    changements.to_csv(path, index=False)

def est_direction_conservee(row, directions_conservees=None):
    """Vérifier si un changement de direction est déjà validé"""
    if directions_conservees is None:
        directions_conservees = charger_directions_conservees()
    
    f = (
        (directions_conservees['direction_extraction'] == row['direction']) &
        (directions_conservees['direction_rh'] == row['direction_rh'])
    )
    return directions_conservees[f].shape[0] > 0
