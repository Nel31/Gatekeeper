# gatekeeper/tools.py
import re
from unidecode import unidecode
from rapidfuzz import fuzz

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

def alias_match(value: str, aliases: list) -> bool:
    val = normalize_text(value)
    return any(val == normalize_text(a) for a in aliases)
