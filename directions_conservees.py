import pandas as pd
from datetime import datetime
import os

CSV_DIRECTIONS = "directions_conservees.csv"

def charger_directions_conservees(path=CSV_DIRECTIONS):
    if not os.path.exists(path):
        return pd.DataFrame(columns=["direction_extraction", "direction_rh", "date_validation", "certificateur"])
    return pd.read_csv(path)

def est_direction_conservee(row, directions_conservees):
    f = (
        (directions_conservees['direction_extraction'] == row['direction']) &
        (directions_conservees['direction_rh'] == row['direction_rh'])
    )
    return directions_conservees[f].shape[0] > 0

def ajouter_direction_conservee(row, certificateur, path=CSV_DIRECTIONS):
    directions_conservees = charger_directions_conservees(path)
    nv = {
        "direction_extraction": row['direction'],
        "direction_rh": row['direction_rh'],
        "date_validation": datetime.now().strftime('%Y-%m-%d'),
        "certificateur": certificateur
    }
    directions_conservees = pd.concat([directions_conservees, pd.DataFrame([nv])], ignore_index=True)
    directions_conservees.drop_duplicates(inplace=True)
    directions_conservees.to_csv(path, index=False)
