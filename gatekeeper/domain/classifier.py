from datetime import datetime

def classify_accounts(df_ext, df_rh):
    rh_ids = set(df_rh['code_utilisateur'])
    in_sgb = []
    out_sgb = []
    now = datetime.now()
    for row in df_ext.to_dict(orient='records'):
        delta = (now - row['derniere_connexion']).days if row['derniere_connexion'] else None
        if row['code_utilisateur'] in rh_ids:
            row['statut'] = 'never-used' if row['derniere_connexion'] is None else ('dormant' if delta > 120 else 'active')
            in_sgb.append(row)
        else:
            out_sgb.append(row)
    return pd.DataFrame(in_sgb), pd.DataFrame(out_sgb)
