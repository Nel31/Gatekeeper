import pandas as pd
from gatekeeper.domain.report_builder import build_report

def test_build_report(sample_rh):
    df_in = pd.DataFrame({
        'code_utilisateur': ['U001'],
        'profil': ['Dev'],
    })
    df_rh = sample_rh()
    df_rh['profil'] = ['Dev']
    rpt = build_report(df_in, df_rh)
    assert 'code_utilisateur' in rpt.columns
