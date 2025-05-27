import yaml
import unicodedata
import re

def load_column_aliases(path='config/column_aliases.yml'):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def normalize_colname(name):
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode()
    name = name.lower().replace(" ", "_")
    name = re.sub(r'[^a-z0-9_]', '', name)
    return name

def auto_rename_columns(df, col_aliases):
    alias_map = {}
    for canon, variants in col_aliases.items():
        for v in variants:
            alias_map[normalize_colname(v)] = canon
        alias_map[normalize_colname(canon)] = canon
    new_cols = {}
    for c in df.columns:
        key = normalize_colname(c)
        if key in alias_map:
            new_cols[c] = alias_map[key]
        else:
            new_cols[c] = c
    return df.rename(columns=new_cols)
