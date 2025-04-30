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
