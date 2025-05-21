# gatekeeper/config.py
from pydantic import BaseSettings
import yaml

class Settings(BaseSettings):
    threshold_days_inactive: int = 120
    class Config:
        env_file = ".env"

settings = Settings()

with open('config/column_aliases.yml') as f:
    column_alias_map = yaml.safe_load(f)
with open('config/profile_aliases.yml') as f:
    profile_alias_map = yaml.safe_load(f)
