import re
import unicodedata

def normalize(text: str) -> str:
    txt = text.strip().lower()
    txt = ''.join(c for c in unicodedata.normalize('NFD', txt) if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', '_', txt)

def normalize_text(txt: str) -> str:
    return normalize(txt)
