import pandas as pd

def associer_rh_aux_utilisateurs(ext_df, rh_df):
    merged = ext_df.merge(
        rh_df.rename(columns={
            'profil': 'profil_rh',
            'direction': 'direction_rh',
            'nom_prenom': 'nom_prenom_rh'
        }),
        how='left',
        on='code_utilisateur'
    )
    merged['compte_non_rh'] = merged['profil_rh'].isnull()
    merged['nom_prenom'] = merged.apply(
        lambda row: row['nom_prenom_rh'] if (pd.isna(row['nom_prenom']) or row['nom_prenom'] in ['', 'nan']) else row['nom_prenom'],
        axis=1
    )
    return merged
