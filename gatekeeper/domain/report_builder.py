import pandas as pd

def build_report(df_in, df_rh):
    merged = df_rh.merge(df_in, on='code_utilisateur', how='inner', suffixes=('', '_ext'))
    cols = [
        'code_utilisateur', 'nom', 'prenom', 'profil_ext', 'direction',
        'recommandation', 'commentaire_revue', 'certificateur', 'decision',
        'commentaire_certificateur', 'execution', 'execute_par', 'commentaire_execution'
    ]
    report = merged[cols].copy()
    report.columns = [c.replace('_ext', '') for c in cols]
    return report
