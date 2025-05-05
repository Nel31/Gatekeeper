# gatekeeper/validator.py
import re
from unidecode import unidecode
from rapidfuzz import fuzz
import pandas as pd
from .config import COLUMN_ALIASES

def normalize(header: str) -> str:
    h = unidecode(header or "")
    return re.sub(r'[^a-z0-9]', '', h.lower())

def validate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    expected = {'cuti', 'last_login', 'extraction_date', 'lib', 'lputi', 'status'}
    mapping = {}
    for col in df.columns:
        norm = normalize(col)
        best_score, best_key = 0, None
        for key in expected:
            for alias_norm in COLUMN_ALIASES.get(key, []):
                score = fuzz.ratio(norm, alias_norm)
                if score > best_score:
                    best_score, best_key = score, key
        if best_score >= 80:
            mapping[col] = best_key
    df = df.rename(columns=mapping)
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"Missing extraction columns: {missing}")
    return df[list(expected)]

def validate_rh_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    expected = {'rh_id', 'last_name', 'first_name', 'position', 'direction'}
    mapping = {}
    for col in df.columns:
        norm = normalize(col)
        best_score, best_key = 0, None
        for key in expected:
            for alias_norm in COLUMN_ALIASES.get(key, []):
                score = fuzz.ratio(norm, alias_norm)
                if score > best_score:
                    best_score, best_key = score, key
        if best_score >= 80:
            mapping[col] = best_key
    df = df.rename(columns=mapping)
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"Missing RH columns: {missing}")
    return df[list(expected)]
