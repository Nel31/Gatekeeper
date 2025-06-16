import yaml
from core.text_utils import normalize_column_name, is_similar

def load_column_aliases(path='config/column_aliases.yml'):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def auto_rename_columns(df, col_aliases, threshold=85):
    alias_map = {}
    canon_names = set()
    for canon, variants in col_aliases.items():
        canon_names.add(canon)
        for v in variants:
            alias_map[normalize_column_name(v)] = canon
        alias_map[normalize_column_name(canon)] = canon

    all_keys = list(alias_map.keys())
    new_cols = {}
    for c in df.columns:
        key = normalize_column_name(c)
        # 1. Correspondance exacte
        if key in alias_map:
            new_cols[c] = alias_map[key]
            continue
        # 2. Fuzzy matching sur les alias connus
        best_score = 0
        best_canon = None
        for alias_key in all_keys:
            if is_similar(key, alias_key, threshold):
                best_canon = alias_map[alias_key]
                break
        if best_canon:
            new_cols[c] = best_canon
        else:
            new_cols[c] = c  # Pas de mapping trouvé, garder le nom original
    return df.rename(columns=new_cols)
