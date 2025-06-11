import yaml
import unicodedata
import re
from rapidfuzz import fuzz

def load_column_aliases(path='config/column_aliases.yml'):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def normalize_colname(name):
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode()
    name = name.lower().replace(" ", "_")
    name = re.sub(r'[^a-z0-9_]', '', name)
    return name

def auto_rename_columns(df, col_aliases, threshold=85):
    alias_map = {}
    canon_names = set()
    for canon, variants in col_aliases.items():
        canon_names.add(canon)
        for v in variants:
            alias_map[normalize_colname(v)] = canon
        alias_map[normalize_colname(canon)] = canon

    all_keys = list(alias_map.keys())
    new_cols = {}
    for c in df.columns:
        key = normalize_colname(c)
        # 1. Correspondance exacte
        if key in alias_map:
            new_cols[c] = alias_map[key]
            continue
        # 2. Fuzzy matching sur les alias connus
        best_score = 0
        best_canon = None
        for alias_key in all_keys:
            score = fuzz.ratio(key, alias_key)
            if score > best_score:
                best_score = score
                best_canon = alias_map[alias_key]
        if best_score >= threshold:
            new_cols[c] = best_canon
        else:
            new_cols[c] = c  # Pas de mapping trouvé, garder le nom original
    return df.rename(columns=new_cols)
