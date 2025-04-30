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
