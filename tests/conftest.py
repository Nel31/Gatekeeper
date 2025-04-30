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
