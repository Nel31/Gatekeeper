# gatekeeper/cleaner.py
import pandas as pd
from unidecode import unidecode

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    for col in ['lib', 'lputi', 'status']:
        df[col] = df[col].astype(str).map(lambda s: unidecode(s).strip().lower())
    df['last_login'] = pd.to_datetime(df['last_login'], format='%Y-%m-%d', errors='coerce')
    df['extraction_date'] = pd.to_datetime(df['extraction_date'], format='%Y-%m-%d', errors='coerce')
    df['status'] = df['status'].map({'oui':'suspendu','non':'actif'}).fillna(df['status'])
    return df[df['status']!='suspendu']
