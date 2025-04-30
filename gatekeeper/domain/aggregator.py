import pandas as pd

def aggregate_and_detect(df: pd.DataFrame):
    anomalies = []
    grouped = []
    for key, grp in df.groupby('code_utilisateur'):
        last = grp.loc[grp['derniere_connexion'].idxmax()]
        for col in ['lib', 'lputi', 'suspendu']:
            if grp[col].nunique() > 1:
                anomalies.append((key, col, grp[col].unique().tolist()))
        grouped.append(last)
    return pd.DataFrame(grouped), anomalies
