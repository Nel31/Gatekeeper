import re
from unidecode import unidecode
from rapidfuzz import fuzz, process

TH_HIGH = 90
TH_LOW = 60

def normalize_header(header: str) -> str:
    text = unidecode(header or "")
    return re.sub(r'[^a-z0-9]', '', text.lower())

def find_best_alias(norm: str, alias_map: dict) -> str:
    best_score, best_key = 0, None
    for key, aliases in alias_map.items():
        for alias in aliases:
            score = fuzz.ratio(norm, normalize_header(alias))
            if score > best_score:
                best_score, best_key = score, key
    return best_key if best_score >= 80 else None

def normalize_text(text: str) -> str:
    return re.sub(r'[^a-z0-9]', '', unidecode(text or "").strip().lower())

from typing import List, Tuple
import os
import pandas as pd

def fuzzy_map(value: str, candidates: List[str]) -> Tuple[str,int]:
    match, score, _ = process.extractOne(
        value, candidates, scorer=fuzz.WRatio
    )
    return match, score


def enrich_mapping(
    df: pd.DataFrame,
    col_ext: str,
    candidates: List[str],
    map_path: str
) -> pd.DataFrame:
    if os.path.exists(map_path):
        map_df = pd.read_csv(map_path)
    else:
        map_df = pd.DataFrame(columns=['value_ext','mapped_canon','score'])
    mapping = dict(zip(map_df['value_ext'], map_df['mapped_canon']))
    new_vals = set(df[col_ext].dropna().unique()) - set(mapping.keys())
    updates = []
    for val in new_vals:
        match, score = fuzzy_map(val, list(candidates))
        if score >= TH_HIGH:
            canon = match
        elif score >= TH_LOW:
            canon = f"{match} ({score}%)"
        else:
            canon = None
        mapping[val] = canon or val
        updates.append({'value_ext': val, 'mapped_canon': mapping[val], 'score': score})
    if updates:
        map_df = pd.concat([map_df, pd.DataFrame(updates)], ignore_index=True)
        map_df.to_csv(map_path, index=False)
    df[f'{col_ext}_mapped'] = df[col_ext].map(lambda x: mapping.get(x, x))
    return df
