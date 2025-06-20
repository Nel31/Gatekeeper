from config.constants import COLUMN_ALIASES
from core.text_utils import normalize_column_name, is_similar


def load_column_aliases(path=None):
    """
    Charger les alias de colonnes
    Maintenu pour compatibilité mais n'utilise plus de fichier
    """
    return COLUMN_ALIASES


def auto_rename_columns(df, col_aliases=None, threshold=85):
    """
    Renommer automatiquement les colonnes selon les alias
    """
    if col_aliases is None:
        col_aliases = COLUMN_ALIASES

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