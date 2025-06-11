import yaml
import unicodedata
import re
from rapidfuzz import process, fuzz

def load_column_aliases(path='config/column_aliases.yml'):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def normalize_colname(name):
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode()
    name = name.lower().replace(" ", "_")
    name = re.sub(r'[^a-z0-9_]', '', name)
    return name

def auto_rename_columns(df, col_aliases, threshold=80):
    # Préparation des noms normalisés pour le fuzzy matching
    normalized_aliases = {}
    for canon, variants in col_aliases.items():
        normalized_variants = [normalize_colname(v) for v in variants]
        normalized_variants.append(normalize_colname(canon))
        normalized_aliases[canon] = normalized_variants

    new_cols = {}
    for col in df.columns:
        normalized_col = normalize_colname(col)
        best_match = None
        best_score = 0
        best_canon = None

        # Recherche du meilleur match pour chaque nom canonique
        for canon, variants in normalized_aliases.items():
            for variant in variants:
                score = fuzz.ratio(normalized_col, variant)
                if score > best_score:
                    best_score = score
                    best_match = variant
                    best_canon = canon

        # Si le score est supérieur au seuil, on utilise le nom canonique
        if best_score >= threshold:
            new_cols[col] = best_canon
        else:
            new_cols[col] = col

    return df.rename(columns=new_cols)
