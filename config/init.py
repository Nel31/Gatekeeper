# gatekeeper/config/__init__.py

import yaml
from pathlib import Path

with open(Path(__file__).parent / "column_aliases.yml", encoding="utf-8") as f:
    column_alias_map = yaml.safe_load(f)
