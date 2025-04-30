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
