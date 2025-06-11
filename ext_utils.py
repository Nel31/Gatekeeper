import pandas as pd
from column_mapping import load_column_aliases, auto_rename_columns

col_aliases = load_column_aliases('config/column_aliases.yml')

def robust_datetime_parse(series):
    parsed = pd.to_datetime(series, errors='coerce')
    if parsed.isna().any():
        parsed = pd.to_datetime(series, errors='coerce', dayfirst=True)
    return parsed

def charger_et_preparer_ext(fichier_ext):
    df = pd.read_excel(fichier_ext)
    df = auto_rename_columns(df, col_aliases)
    
    # Filtrage comptes suspendus/désactivés
    if 'status' in df.columns:
        status_col = 'status'
        # Normalise en string
        df[status_col] = df[status_col].astype(str).str.strip().str.lower()
        # Liste des valeurs qui signifient "suspendu" ou "désactivé"
        valeurs_non_actives = {
            '1', 'oui', 'true', 'vrai',
            'suspendu', 'désactive', 'désactivé', 'desactive', 'inactive', 'locked', 'supprimé', 'supprime', 'deleted', 'archive'
        }
        # On retire tout ce qui n’est pas clairement actif/0/non
        df = df[~df[status_col].isin(valeurs_non_actives)].copy()
    else:
        print("Alerte : colonne 'status' absente après mapping, aucun filtrage suspendu.")

    # Traitement des dates
    for datecol in ['last_login', 'extraction_date']:
        if datecol in df.columns:
            df[datecol] = robust_datetime_parse(df[datecol])
    # Normalisation des autres colonnes texte
    for txtcol in ['nom_prenom', 'profil', 'direction', 'status']:
        if txtcol in df.columns:
            df[txtcol] = df[txtcol].astype(str).str.strip().str.lower()
    return df
