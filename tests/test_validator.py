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
