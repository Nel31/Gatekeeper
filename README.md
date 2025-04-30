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
