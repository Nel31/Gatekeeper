import datetime
import pandera as pa
from pandera import Column, Check, DataFrameSchema

# Schéma extraction applicative
ext_schema = DataFrameSchema({
    "code_utilisateur": Column(str, nullable=False),
    "nom_prenom":       Column(str, nullable=True),
    "profil":           Column(str, nullable=True),
    "direction":        Column(str, nullable=True),
    "last_login":       Column(pa.DateTime, nullable=False),
    "extraction_date":  Column(pa.DateTime, nullable=False,
                               checks=Check(lambda s: s >= datetime.datetime(1900,1,1))),
    "status":           Column(str, nullable=False),
}, coerce=True)

# Schéma RH
rh_schema = DataFrameSchema({
    "code_utilisateur": Column(str, nullable=False),
    "last_name":        Column(str, nullable=True),
    "first_name":       Column(str, nullable=True),
    "position":         Column(str, nullable=True),
    "direction":        Column(str, nullable=True),
}, coerce=True)