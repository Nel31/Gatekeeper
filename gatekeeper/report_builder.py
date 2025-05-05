# gatekeeper/report_builder.py
import pandas as pd
from rapidfuzz import fuzz
from .config import settings

def build_report(df: pd.DataFrame, certificateur: str) -> pd.DataFrame:
    in_sgb = df[df['category']=='in_sgb'].copy()
    in_sgb['full_name'] = (
        in_sgb['last_name'].str.strip() + ' ' + in_sgb['first_name'].str.strip()
    )
    report = in_sgb[[
        'rh_id','full_name','position','direction',
        'days_inactive','lputi_extracted'
    ]].copy()
    report.rename(columns={
        'rh_id':'code_utilisateur',
        'full_name':'nom_prenom',
        'position':'profil',
        'direction':'direction'
    }, inplace=True)
    report['recommandation'] = 'A certifier'
    report['certificateur'] = certificateur
    report['décision'] = report['days_inactive'].apply(
        lambda d: 'A désactiver' if d>settings.threshold_days_inactive else 'A conserver'
    )

    def exec_status(row):
        if row['décision']=='A désactiver':
            return 'Désactivé'
        score = fuzz.token_sort_ratio(
            row['profil'].strip().lower(),
            row['lputi_extracted'].strip().lower()
        )
        if score < 85:
            return 'Modifié'
        return 'Conservé'

    report['exécution'] = report.apply(exec_status, axis=1)

    for col in [
        'commentaire_revue','commentaire_certificateur',
        'exécuté_par','commentaire_exécution'
    ]:
        report[col] = ''
    return report.drop(columns=['days_inactive','lputi_extracted'])
