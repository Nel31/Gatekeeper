# gatekeeper/config.py
from pydantic import BaseSettings
import re
from unidecode import unidecode

class Settings(BaseSettings):
    threshold_days_inactive: int = 120

    class Config:
        env_file = ".env"

settings = Settings()

RAW_COLUMN_ALIASES = {
    'cuti': ['CUTI', 'Identifiant Applicatif', 'applicationID'],
    'last_login': ['DATE DERNIÈRE CONNEXION', 'DateConnexion', 'Date_Derniere_Connexion'],
    'extraction_date': ['DATE_EXTRACTION', 'DateExtraction', 'date_extraction'],
    'lib': ['LIB', 'Libellé', 'Label'],
    'lputi': ['LPUTI', 'Intitulé Métier', 'intituleposte'],
    'status': ['SUS', 'Statut', 'Suspendu', 'oui', 'non'],
    'rh_id': ['Identifiant Local', 'IdentifiantInterne', 'IDInterne'],
    'last_name': ['Nom', 'Nom de Famille'],
    'first_name': ['Prénom(s)', 'Prenom(s)', 'Prenoms'],
    'position': ['Intitulé du poste', 'Poste', 'intituleduposte'],
    'direction': ['Direction'],
}

def _normalize_alias(alias: str) -> str:
    h = unidecode(alias or "")
    return re.sub(r'[^a-z0-9]', '', h.lower())

COLUMN_ALIASES = {
    key: [_normalize_alias(a) for a in vals]
    for key, vals in RAW_COLUMN_ALIASES.items()
}
