# gatekeeper/cleaner.py
import pandas as pd
from unidecode import unidecode

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # Standardize text columns and remove suspended
    for col in ['lib', 'lputi', 'status']:
        df[col] = df[col].astype(str).map(lambda s: unidecode(s).strip().lower())
    df['last_login'] = pd.to_datetime(df['last_login'], errors='coerce')
    df['extraction_date'] = pd.to_datetime(df['extraction_date'], errors='coerce')
    df = df[df['status'].map({'oui':'suspendu','non':'actif'}).fillna(df['status']) != 'suspendu']
    return df
