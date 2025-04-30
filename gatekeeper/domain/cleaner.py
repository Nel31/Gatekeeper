import pandas as pd
from gatekeeper.services.utils import normalize_text

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.select_dtypes(include=[object]).columns:
        df[col] = df[col].fillna("").astype(str).apply(normalize_text)
    df['derniere_connexion'] = pd.to_datetime(df['derniere_connexion'], errors='coerce')
    return df[df.get('suspendu', False) != True]
