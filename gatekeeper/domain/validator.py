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
