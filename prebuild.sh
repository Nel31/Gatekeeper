#!/usr/bin/env bash
set -euo pipefail

# Création des répertoires
mkdir -p config \
         gatekeeper/adapters \
         gatekeeper/domain \
         gatekeeper/services \
         tests

# .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: stable
    hooks:
      - id: black
  - repo: https://gitlab.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
EOF

# config/default.yaml
cat > config/default.yaml << 'EOF'
inactivity_threshold_days: 120
column_mappings:
  code_utilisateur: ["code utilisateur", "cuti", "identifiant utilisateur"]
  nom: ["nom"]
  prenom: ["prénom", "prenom"]
  direction: ["direction"]
  derniere_connexion: ["date dernière connexion", "last_login"]
EOF

# requirements.txt
cat > requirements.txt << 'EOF'
pandas>=1.5
openpyxl
pandera
click
pytest
coverage
EOF

# setup.cfg
cat > setup.cfg << 'EOF'
[flake8]
max-line-length = 88
exclude = .venv,build,dist
EOF

# pyproject.toml
cat > pyproject.toml << 'EOF'
[tool.poetry]
name = "gatekeeper"
version = "0.1.0"
description = "Revue périodique des comptes utilisateurs"
authors = ["Ornel Whannou <user@example.com>"]

[tool.poetry.dependencies]
python = "^3.9"
pandas = "^1.5"
openpyxl = "*"
pandera = "*"
click = "*"

[tool.poetry.dev-dependencies]
pytest = "*"
flake8 = "*"
black = "*"
pre-commit = "*"
EOF

# README.md
cat > README.md << 'EOF'
# Gatekeeper

Pipeline de revue des comptes utilisateurs (In SGB / Out SGB).

## Installation

\`\`\`bash
git clone https://.../gatekeeper.git
cd gatekeeper
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pre-commit install
\`\`\`

## Usage

\`\`\`bash
gatekeeper --rh-file rh.xlsx --ext-file ext.xlsx --template template.xlsx --output rapport.xlsx
\`\`\`
EOF

# gatekeeper/main.py
cat > gatekeeper/main.py << 'EOF'
import click
from gatekeeper.services.orchestrator import run_pipeline

@click.command()
@click.option("--rh-file", required=True, type=click.Path(exists=True))
@click.option("--ext-file", required=True, type=click.Path(exists=True))
@click.option("--template", required=True, type=click.Path(exists=True))
@click.option("--output", required=True, type=click.Path())
def main(rh_file, ext_file, template, output):
    """
    Lance la revue Gatekeeper : RH + extractions → rapport Excel.
    """
    run_pipeline(rh_file, ext_file, template, output)

if __name__ == "__main__":
    main()
EOF

# gatekeeper/services/orchestrator.py
cat > gatekeeper/services/orchestrator.py << 'EOF'
import sys
from gatekeeper.adapters.excel_reader import read_excel
from gatekeeper.adapters.excel_writer import write_excel
from gatekeeper.domain.validator import validate_and_normalize
from gatekeeper.domain.cleaner import clean_dataframe
from gatekeeper.domain.aggregator import aggregate_and_detect
from gatekeeper.domain.classifier import classify_accounts
from gatekeeper.domain.duplicates import detect_duplicates
from gatekeeper.domain.report_builder import build_report

def run_pipeline(rh_path, ext_path, tpl_path, out_path):
    df_rh   = read_excel(rh_path)
    df_ext  = read_excel(ext_path)
    df_tpl  = read_excel(tpl_path)

    df_rh = validate_and_normalize(df_rh)
    df_ext = validate_and_normalize(df_ext)

    df_ext_clean = clean_dataframe(df_ext)
    df_agg, anomalies = aggregate_and_detect(df_ext_clean)
    in_sgb, out_sgb = classify_accounts(df_agg, df_rh)

    duplicates = detect_duplicates(in_sgb)
    if duplicates:
        print("Doublons détectés : ", duplicates)
        sys.exit(84)

    report_df = build_report(in_sgb, df_rh)
    write_excel(out_path, report_df, tpl_path)

    print("Pipeline exécuté avec succès.")
EOF

# gatekeeper/adapters/excel_reader.py
cat > gatekeeper/adapters/excel_reader.py << 'EOF'
import pandas as pd

def read_excel(path: str) -> pd.DataFrame:
    return pd.read_excel(path)
EOF

# gatekeeper/adapters/excel_writer.py
cat > gatekeeper/adapters/excel_writer.py << 'EOF'
from openpyxl import load_workbook
import pandas as pd

def write_excel(out_path: str, df: pd.DataFrame, template_path: str):
    wb = load_workbook(template_path)
    ws = wb.active
    for r_idx, row in enumerate(df.itertuples(index=False), start=2):
        for c_idx, value in enumerate(row, start=1):
            ws.cell(row=r_idx, column=c_idx, value=value)
    wb.save(out_path)
EOF

# gatekeeper/domain/validator.py
cat > gatekeeper/domain/validator.py << 'EOF'
import pandas as pd
import pandera as pa
from pandera import Column, DataFrameSchema
from gatekeeper.services.utils import normalize

class InputSchema(DataFrameSchema):
    code_utilisateur = Column(pa.String, nullable=False)
    nom = Column(pa.String, nullable=False)
    prenom = Column(pa.String, nullable=False)
    direction = Column(pa.String, nullable=False)

def validate_and_normalize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=lambda c: normalize(c))
    schema = InputSchema()
    return schema(df)
EOF

# gatekeeper/domain/cleaner.py
cat > gatekeeper/domain/cleaner.py << 'EOF'
import pandas as pd
from gatekeeper.services.utils import normalize_text

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.select_dtypes(include=[object]).columns:
        df[col] = df[col].fillna("").astype(str).apply(normalize_text)
    df['derniere_connexion'] = pd.to_datetime(df['derniere_connexion'], errors='coerce')
    return df[df.get('suspendu', False) != True]
EOF

# gatekeeper/domain/aggregator.py
cat > gatekeeper/domain/aggregator.py << 'EOF'
import pandas as pd

def aggregate_and_detect(df: pd.DataFrame):
    anomalies = []
    grouped = []
    for key, grp in df.groupby('code_utilisateur'):
        last = grp.loc[grp['derniere_connexion'].idxmax()]
        for col in ['lib', 'lputi', 'suspendu']:
            if grp[col].nunique() > 1:
                anomalies.append((key, col, grp[col].unique().tolist()))
        grouped.append(last)
    return pd.DataFrame(grouped), anomalies
EOF

# gatekeeper/domain/classifier.py
cat > gatekeeper/domain/classifier.py << 'EOF'
from datetime import datetime

def classify_accounts(df_ext, df_rh):
    rh_ids = set(df_rh['code_utilisateur'])
    in_sgb = []
    out_sgb = []
    now = datetime.now()
    for row in df_ext.to_dict(orient='records'):
        delta = (now - row['derniere_connexion']).days if row['derniere_connexion'] else None
        if row['code_utilisateur'] in rh_ids:
            row['statut'] = 'never-used' if row['derniere_connexion'] is None else ('dormant' if delta > 120 else 'active')
            in_sgb.append(row)
        else:
            out_sgb.append(row)
    return pd.DataFrame(in_sgb), pd.DataFrame(out_sgb)
EOF

# gatekeeper/domain/duplicates.py
cat > gatekeeper/domain/duplicates.py << 'EOF'
from collections import Counter

def detect_duplicates(df):
    names = df['nom'] + ' ' + df['prenom']
    c = Counter(names)
    return [name for name, count in c.items() if count > 1]
EOF

# gatekeeper/domain/report_builder.py
cat > gatekeeper/domain/report_builder.py << 'EOF'
import pandas as pd

def build_report(df_in, df_rh):
    merged = df_rh.merge(df_in, on='code_utilisateur', how='inner', suffixes=('', '_ext'))
    cols = [
        'code_utilisateur', 'nom', 'prenom', 'profil_ext', 'direction',
        'recommandation', 'commentaire_revue', 'certificateur', 'decision',
        'commentaire_certificateur', 'execution', 'execute_par', 'commentaire_execution'
    ]
    report = merged[cols].copy()
    report.columns = [c.replace('_ext', '') for c in cols]
    return report
EOF

# gatekeeper/services/utils.py
cat > gatekeeper/services/utils.py << 'EOF'
import re
import unicodedata

def normalize(text: str) -> str:
    txt = text.strip().lower()
    txt = ''.join(c for c in unicodedata.normalize('NFD', txt) if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', '_', txt)

def normalize_text(txt: str) -> str:
    return normalize(txt)
EOF

# tests/conftest.py
cat > tests/conftest.py << 'EOF'
import pytest
import pandas as pd

@pytest.fixture
def sample_rh():
    return pd.DataFrame({
        'code_utilisateur': ['U001'],
        'nom': ['Dupont'],
        'prenom': ['Alice'],
        'direction': ['IT'],
    })
EOF

# tests/test_validator.py
cat > tests/test_validator.py << 'EOF'
import pandas as pd
import pytest
from gatekeeper.domain.validator import validate_and_normalize

def test_validate_and_normalize(sample_rh):
    df = pd.DataFrame({
        'Code Utilisateur': ['U001'],
        'Nom ': ['Dupont'],
        'Prénom': ['Alice'],
        'Direction': ['IT']
    })
    out = validate_and_normalize(df)
    assert list(out.columns) == ['code_utilisateur', 'nom', 'prenom', 'direction']
EOF

# tests/test_cleaner.py
cat > tests/test_cleaner.py << 'EOF'
import pandas as pd
from gatekeeper.domain.cleaner import clean_dataframe

def test_clean_dataframe():
    df = pd.DataFrame({
        'code_utilisateur': ['U001'],
        'nom': [' Dupont '],
        'derniere_connexion': ['2025-01-01'],
        'suspendu': [False]
    })
    out = clean_dataframe(df)
    assert out.iloc[0]['nom'] == 'dupont'
EOF

# tests/test_aggregator.py
cat > tests/test_aggregator.py << 'EOF'
import pandas as pd
from gatekeeper.domain.aggregator import aggregate_and_detect

def test_aggregate_and_detect():
    df = pd.DataFrame({
        'code_utilisateur': ['U1','U1'],
        'derniere_connexion': ['2025-01-01','2025-02-01'],
        'lib': ['A','B'],
        'lputi': ['X','X'],
        'suspendu': [False, False]
    })
    agg, anomalies = aggregate_and_detect(df)
    assert len(agg)==1
    assert anomalies
EOF

# tests/test_classifier.py
cat > tests/test_classifier.py << 'EOF'
import pandas as pd
from gatekeeper.domain.classifier import classify_accounts

def test_classify_accounts(sample_rh):
    df_ext = pd.DataFrame({
        'code_utilisateur': ['U001','U002'],
        'derniere_connexion': [pd.NaT, pd.Timestamp('2025-04-01')]
    })
    in_sgb, out_sgb = classify_accounts(df_ext, sample_rh)
    assert 'never-used' in in_sgb['statut'].values
    assert not out_sgb.empty
EOF

# tests/test_duplicates.py
cat > tests/test_duplicates.py << 'EOF'
import pandas as pd
from gatekeeper.domain.duplicates import detect_duplicates

def test_detect_duplicates():
    df = pd.DataFrame({'nom': ['A','A'], 'prenom': ['X','X']})
    dups = detect_duplicates(df)
    assert dups == ['A X']
EOF

# tests/test_report_builder.py
cat > tests/test_report_builder.py << 'EOF'
import pandas as pd
from gatekeeper.domain.report_builder import build_report

def test_build_report(sample_rh):
    df_in = pd.DataFrame({
        'code_utilisateur': ['U001'],
        'profil': ['Dev'],
    })
    df_rh = sample_rh()
    df_rh['profil'] = ['Dev']
    rpt = build_report(df_in, df_rh)
    assert 'code_utilisateur' in rpt.columns
EOF

echo "Structure du projet Gatekeeper créée avec succès !"
