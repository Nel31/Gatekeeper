# gatekeeper/report_builder.py
import pandas as pd
from rapidfuzz import fuzz
from .config import settings

def build_report(classified: pd.DataFrame, certificateur: str) -> pd.DataFrame:
    columns = [
        'code_utilisateur','nom_prenom','profil','direction',
        'recommandation','commentaire_revue','certificateur',
        'décision','exécution','exécuté_par','commentaire_exécution'
    ]
    rows = []
    for _, r in classified.iterrows():
        code = r['cuti']
        cat = r['category']
        nom_prenom = profil = direction = ''
        recommandation = 'A certifier'
        commentaire_revue = ''
        décision = exécution = exécuté_par = commentaire_exécution = ''
        # In SGB
        if cat=='in_sgb':
            nom_prenom = f"{r['last_name'].strip()} {r['first_name'].strip()}"
            profil = r['position']
            direction = r['direction']
            décision = 'A désactiver' if r['days_inactive']>settings.threshold_days_inactive else 'A conserver'
            if décision=='A désactiver':
                exécution = 'Désactivé'
            else:
                score = fuzz.token_sort_ratio(profil.lower().strip(), r['lputi_extracted'].lower().strip())
                exécution = 'Modifié' if score<85 else 'Conservé'
        # Out SGB: décisions manuelles
        rows.append({
            'code_utilisateur':code,'nom_prenom':nom_prenom,'profil':profil,'direction':direction,
            'recommandation':recommandation,'commentaire_revue':commentaire_revue,'certificateur':certificateur,
            'décision':décision,'exécution':exécution,'exécuté_par':exécuté_par,'commentaire_exécution':commentaire_exécution
        })
    return pd.DataFrame(rows,columns=columns)
