import pandas as pd
from mapping.column_mapping import auto_rename_columns
from config.constants import COLUMN_ALIASES

def charger_et_preparer_rh(fichiers_rh):
    dfs = []
    for f in fichiers_rh:
        df = pd.read_excel(f)
        df = auto_rename_columns(df, COLUMN_ALIASES)
        if 'nom_prenom' not in df.columns or df['nom_prenom'].isnull().any():
            if 'first_name' in df.columns and 'last_name' in df.columns:
                df['nom_prenom'] = df['first_name'].fillna('') + ' ' + df['last_name'].fillna('')
                df['nom_prenom'] = df['nom_prenom'].str.strip()
            else:
                df['nom_prenom'] = df['nom_prenom'].fillna('')
        useful = [c for c in ['code_utilisateur', 'nom_prenom', 'profil', 'direction'] if c in df.columns]
        df = df[useful].copy()
        dfs.append(df)
    rh_all = pd.concat(dfs).drop_duplicates('code_utilisateur')
    return rh_all