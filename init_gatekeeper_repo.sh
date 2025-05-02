#!/usr/bin/env bash
set -euo pipefail

# Nom du script: init_gatekeeper_repo.sh
# Usage: bash init_gatekeeper_repo.sh

echo "Initialisation du dépôt Gatekeeper…"

# 1. Créer les répertoires
mkdir -p gatekeeper

# 2. Créer les fichiers racine

cat << 'EOF' > requirements.txt
pandas>=1.4
python-dateutil>=2.8
unidecode>=1.3
rapidfuzz>=2.0
pydantic>=1.10
python-dotenv>=0.19
openpyxl>=3.0
XlsxWriter>=3.0
click>=8.0
EOF

cat << 'EOF' > .env.example
# Seuil d'inactivité (jours)
# THRESHOLD_DAYS_INACTIVE=120
EOF

# 3. Créer gatekeeper/__init__.py
touch gatekeeper/__init__.py

# 4. Créer gatekeeper/config.py
cat << 'EOF' > gatekeeper/config.py
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    threshold_days_inactive: int = 120

    class Config:
        env_file = ".env"

settings = Settings()

# Mapping canonical columns to their aliases
COLUMN_ALIASES = {
    'cuti': ['cuti', 'identifiantapplicatif', 'applicationid'],
    'last_login': ['lastlogin', 'dateconnexion', 'date_derniere_connexion'],
    'extraction_date': ['extractiondate', 'dateextraction'],
    'lib': ['lib', 'libelle', 'label'],
    'lputi': ['lputi', 'intitulemétier', 'intituleposte'],
    'status': ['status', 'statut', 'suspendu'],
    'rh_id': ['rh_id', 'identifiantinterne', 'idinterne'],
    'last_name': ['nom'],
    'first_name': ['prenom'],
    'position': ['poste', 'intituleposte'],
    'direction': ['direction']
}
EOF

# 5. Créer gatekeeper/validator.py
cat << 'EOF' > gatekeeper/validator.py
import re
from unidecode import unidecode
from rapidfuzz import fuzz
import pandas as pd
from .config import COLUMN_ALIASES

def normalize(header: str) -> str:
    h = unidecode(header or "")
    return re.sub(r'[^a-z0-9]', '', h.lower())

def validate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {}
    expected = set(COLUMN_ALIASES.keys())

    for col in df.columns:
        norm = normalize(col)
        best_score = 0
        best_key = None
        for key, aliases in COLUMN_ALIASES.items():
            for alias in aliases:
                score = fuzz.ratio(norm, normalize(alias))
                if score > best_score:
                    best_score = score
                    best_key = key
        if best_score >= 80:
            mapping[col] = best_key

    df = df.rename(columns=mapping)
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns after validation: {missing}")
    return df[list(expected)]
EOF

# 6. Créer gatekeeper/cleaner.py
cat << 'EOF' > gatekeeper/cleaner.py
import pandas as pd
from unidecode import unidecode
from .config import settings

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # Normalize text fields
    for col in ['lib', 'lputi', 'status']:
        df[col] = (
            df[col]
            .astype(str)
            .map(lambda s: unidecode(s).strip().lower())
        )
    # Parse dates
    df['last_login'] = pd.to_datetime(df['last_login'], dayfirst=True, errors='coerce')
    df['extraction_date'] = pd.to_datetime(df['extraction_date'], dayfirst=True, errors='coerce')
    # Filter suspended
    df = df[~df['status'].isin(['s', 'suspendu'])]
    return df
EOF

# 7. Créer gatekeeper/aggregator.py
cat << 'EOF' > gatekeeper/aggregator.py
import pandas as pd

def aggregate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.groupby('cuti')
    summary = grp.agg(
        last_login=('last_login', 'max'),
        extraction_date=('extraction_date', 'first'),
        lib_anomaly=('lib', lambda s: s.nunique()>1),
        lputi_anomaly=('lputi', lambda s: s.nunique()>1),
        status_anomaly=('status', lambda s: s.nunique()>1),
    ).reset_index()
    return summary
EOF

# 8. Créer gatekeeper/classifier.py
cat << 'EOF' > gatekeeper/classifier.py
import pandas as pd
import numpy as np
from .config import settings

def classify_accounts(summary: pd.DataFrame, rh: pd.DataFrame) -> pd.DataFrame:
    merged = summary.merge(
        rh, left_on='cuti', right_on='rh_id', how='left', indicator=True
    )
    merged['category'] = merged['_merge'].map({'both':'in_sgb','left_only':'out_sgb'})
    merged['days_inactive'] = (
        merged['extraction_date'] - merged['last_login']
    ).dt.days.fillna(np.inf)
    def label(row):
        if pd.isna(row['last_login']):
            return 'never_used'
        return 'dormant' if row['days_inactive'] > settings.threshold_days_inactive else 'active'
    merged['in_sgb_status'] = merged.apply(label, axis=1)
    return merged
EOF

# 9. Créer gatekeeper/duplicate_detector.py
cat << 'EOF' > gatekeeper/duplicate_detector.py
import sys
import pandas as pd

def check_duplicates(df: pd.DataFrame):
    in_sgb = df[df['category']=='in_sgb']
    in_sgb['full_name'] = (
        in_sgb['last_name'].astype(str) + ' ' + in_sgb['first_name'].astype(str)
    )
    dupes = in_sgb['full_name'].value_counts()
    dupes = dupes[dupes > 1]
    if not dupes.empty:
        print(f"Duplicate accounts found for: {dupes.to_dict()}")
        sys.exit(84)
EOF

# 10. Créer gatekeeper/report_builder.py
cat << 'EOF' > gatekeeper/report_builder.py
import pandas as pd

def build_report(df: pd.DataFrame) -> pd.DataFrame:
    in_sgb = df[df['category']=='in_sgb']
    report = in_sgb[['rh_id','full_name','position','direction']].copy()
    report = report.rename(columns={
        'rh_id':'code_utilisateur',
        'full_name':'nom_prenom',
        'position':'profil',
        'direction':'direction'
    })
    for col in [
        'recommandation','commentaire_revue','certificateur',
        'décision','commentaire_certificateur','exécution',
        'exécuté_par','commentaire_exécution'
    ]:
        report[col] = ''
    return report
EOF

# 11. Créer gatekeeper/injector.py
cat << 'EOF' > gatekeeper/injector.py
from openpyxl import load_workbook

def inject_to_template(report, template_path: str, output_path: str):
    wb = load_workbook(template_path)
    ws = wb.active
    for i, row in enumerate(report.itertuples(index=False), start=2):
        for j, value in enumerate(row, start=1):
            ws.cell(row=i, column=j, value=value)
    wb.save(output_path)
EOF

# 12. Créer gatekeeper/orchestrator.py
cat << 'EOF' > gatekeeper/orchestrator.py
import logging
import pandas as pd
from .validator import validate_dataframe
from .cleaner import clean_dataframe
from .aggregator import aggregate_dataframe
from .classifier import classify_accounts
from .duplicate_detector import check_duplicates
from .report_builder import build_report
from .injector import inject_to_template

logging.basicConfig(
    filename='gatekeeper.log',
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.INFO
)

def run_pipeline(rh_path: str, ext_path: str, template_path: str, output_path: str):
    # Load
    rh_df = pd.read_excel(rh_path)
    ext_df = pd.read_excel(ext_path)
    # Validate
    rh_df = validate_dataframe(rh_df)
    ext_df = validate_dataframe(ext_df)
    # Clean
    ext_df = clean_dataframe(ext_df)
    # Aggregate & anomalies
    summary = aggregate_dataframe(ext_df)
    # Classify
    classified = classify_accounts(summary, rh_df)
    # Duplicate check
    check_duplicates(classified)
    # Build report
    report = build_report(classified)
    # Inject
    inject_to_template(report, template_path, output_path)
    logging.info(f"Report generated: {output_path} ({len(report)} records)")
EOF

# 13. Créer cli.py
cat << 'EOF' > cli.py
import click
from gatekeeper.orchestrator import run_pipeline
from gatekeeper.config import settings

@click.command()
@click.option('--rh-file', required=True, help='Path to RH Excel file')
@click.option('--ext-file', required=True, help='Path to extraction Excel file')
@click.option('--template', required=True, help='Path to report template XLSX')
@click.option('--output', required=True, help='Path for generated report XLSX')
@click.option('--threshold', type=int, default=None, help='Days inactive threshold')
def main(rh_file, ext_file, template, output, threshold):
    if threshold:
        settings.threshold_days_inactive = threshold
    run_pipeline(rh_file, ext_file, template, output)
    click.echo(f"Report successfully generated at {output}")

if __name__ == '__main__':
    main()
EOF

chmod +x init_gatekeeper_repo.sh
echo "✔ Structure et fichiers créés. N’hésitez pas à adapter le contenu avant votre premier commit."
