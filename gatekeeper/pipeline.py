import pandas as pd
import numpy as np
import re
from .config import column_alias_map, settings
from .schemas import ext_schema, rh_schema
from .tools import normalize_header, find_best_alias, normalize_text, enrich_mapping
from .injector import inject_to_template

# 1. Charger et préparer RH
def load_and_prepare_rh(paths):
    dfs = []
    for p in paths:
        df = pd.read_excel(p)
        mapping = {col: find_best_alias(normalize_header(col), column_alias_map)
                   for col in df.columns}
        df = df.rename(columns={k: v for k, v in mapping.items() if v})
        df = rh_schema.validate(df, lazy=True)
        dfs.append(df)
    rh_all = pd.concat(dfs).drop_duplicates('code_utilisateur')
    return rh_all

# 2. Charger et préparer extraction
def load_and_prepare_ext(path):
    df = pd.read_excel(path)
    mapping = {col: find_best_alias(normalize_header(col), column_alias_map)
               for col in df.columns}
    df = df.rename(columns={k: v for k, v in mapping.items() if v})
    df = ext_schema.validate(df, lazy=True)
    # conserver version brute du nom complet
    df['nom_prenom_raw'] = df['nom_prenom']
    # normalisation des champs
    df['status'] = df['status'].map(normalize_text)
    for col in ['nom_prenom', 'profil', 'direction']:
        df[col] = df[col].map(normalize_text)
    df['last_login'] = pd.to_datetime(
        df['last_login'], errors='raise')
    df['extraction_date'] = pd.to_datetime(
        df['extraction_date'], errors='coerce')
    max_login = df['last_login'].max()
    df['extraction_date'] = df['extraction_date'].fillna(max_login)
    return df[df['status'] != 'oui']

# 3. Agrégation
def aggregate_ext(df):
    grp = df.groupby('code_utilisateur')
    return grp.agg(
        last_login=('last_login', 'max'),
        extraction_date=('extraction_date', 'first'),
        nom_prenom_raw=('nom_prenom_raw', 'first'),
        nom_prenom_ext=('nom_prenom', 'first'),
        nom_prenom_anomaly=('nom_prenom', lambda s: s.nunique() > 1),
        profile_ext=('profil', 'first'),
        profile_anomaly=('profil', lambda s: s.nunique() > 1),
        department_ext=('direction', 'first'),
        dept_anomaly=('direction', lambda s: s.nunique() > 1),
        status_anomaly=('status', lambda s: s.nunique() > 1)
    ).reset_index()

# 4. Enrichissement mapping dynamique
def enrich_dynamic_mapping(summary, rh_all):
    canonical_profiles = set(rh_all['position'].dropna().unique())
    canonical_services = set(rh_all['direction'].dropna().unique())
    summary = enrich_mapping(
        summary, 'profile_ext', canonical_profiles, 'mapping_profiles.csv'
    )
    summary = enrich_mapping(
        summary, 'department_ext', canonical_services, 'mapping_services.csv'
    )
    return summary

# Afficher comparaisons de profils
def display_profile_comparisons(df):
    print("\nComparaison des profils utilisateurs :")
    for _, row in df.iterrows():
        print(
            f"{row['code_utilisateur']}: extrait='{row['profile_ext']}', "
            f"mappé='{row['profile_ext_mapped']}', RH='{row['position']}'"
        )

# 5. Fusion avec RH & calcul inactivité
def enrich_with_rh(summary, rh_all):
    df = summary.merge(
        rh_all, on='code_utilisateur', how='left', suffixes=('', '_rh')
    )
    df['days_inactive'] = (
        df['extraction_date'] - df['last_login']
    ).dt.days.fillna(np.inf)
    return df

# 6. Détection des changements
def detect_changes(df):
    is_service_changed = df['department_ext_mapped'] != df['direction']
    is_profile_changed = df['profile_ext_mapped'] != df['position']
    df['is_modified'] = is_service_changed | (~is_service_changed & is_profile_changed)
    return df

# 7. Décisions
def make_decisions(df):
    df['decision'] = np.where(
        df['days_inactive'] > settings.threshold_days_inactive,
        'A désactiver',
        np.where(df['is_modified'], 'Modifié', 'A conserver')
    )
    df['execution_reco_decision'] = np.where(
        df['decision'] == 'A désactiver', 'Désactivé',
        np.where(df['is_modified'], 'Modifié', 'Conservé')
    )
    return df

# 8. Construction du rapport
def build_report(df, certificateur):
    def strip_ratio(s: str) -> str:
        return re.sub(r"\s*\(\d+(\.\d+)?%\)$", '', s or '')
    rpt = (
        df.assign(
            code_utilisateur=df['code_utilisateur'],
            user_full_name=df['nom_prenom_raw'],
            user_profile=df['profile_ext_mapped'].map(strip_ratio),
            department=df['department_ext_mapped'].map(strip_ratio),
            recommendation='A certifier',
            certificateur=certificateur,
            decision=df['decision'],
            execution_reco_decision=df['execution_reco_decision'],
            comment_review='',
            comment_certificateur='',
            executed_by='',
            execution_comment=''
        )
        .loc[:, [
            'code_utilisateur', 'user_full_name', 'user_profile', 'department',
            'recommendation', 'certificateur', 'decision',
            'execution_reco_decision', 'comment_review', 'comment_certificateur',
            'executed_by', 'execution_comment'
        ]]
    )
    return rpt

# run_pipeline orchestrator
def run_pipeline(rh_files, ext_file, template, output, certificateur, show_comparisons=False):
    rh_all = load_and_prepare_rh(rh_files)
    ext_df = load_and_prepare_ext(ext_file)
    summary = aggregate_ext(ext_df)
    mapped = enrich_dynamic_mapping(summary, rh_all)
    merged = enrich_with_rh(mapped, rh_all)
    if show_comparisons:
        display_profile_comparisons(merged)
    changed = detect_changes(merged)
    decided = make_decisions(changed)
    report = build_report(decided, certificateur)
    inject_to_template(report, template, output)
