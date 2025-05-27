import os

project_root = "gatekeeper"

# Fichiers à créer et leur contenu
files = {
    "main.py": '''
import typer
from rh_utils import charger_et_preparer_rh
from ext_utils import charger_et_preparer_ext
from match_utils import associer_rh_aux_utilisateurs
from anomalies import detecter_anomalies, extraire_cas_a_verifier
from manual_review import traiter_cas_manuels
from report import remplir_template, afficher_resume

app = typer.Typer()

@app.command()
def run(
    rh_files: str = typer.Option(..., help="Fichiers RH, séparés par une virgule"),
    ext_file: str = typer.Option(..., help="Fichier d'extraction applicative"),
    template_file: str = typer.Option(..., help="Template Excel"),
    output_file: str = typer.Option(..., help="Fichier de rapport à générer"),
    cert_name: str = typer.Option(..., help="Nom du certificateur"),
):
    rh_paths = [p.strip() for p in rh_files.split(",")]
    rh_df = charger_et_preparer_rh(rh_paths)
    ext_df = charger_et_preparer_ext(ext_file)
    ext_df = associer_rh_aux_utilisateurs(ext_df, rh_df)
    ext_df = detecter_anomalies(ext_df)
    cas_a_verifier = extraire_cas_a_verifier(ext_df)
    ext_df = traiter_cas_manuels(ext_df, cas_a_verifier)
    rapport = remplir_template(template_file, ext_df, cert_name)
    rapport.to_excel(output_file, index=False)
    afficher_resume(ext_df)

if __name__ == "__main__":
    app()
''',

    "rh_utils.py": '''
import pandas as pd

def charger_et_preparer_rh(fichiers_rh):
    dfs = []
    for f in fichiers_rh:
        df = pd.read_excel(f)
        # Mapping des colonnes (à adapter à ton mapping réel)
        colmap = {c: c.lower().replace(" ", "_") for c in df.columns}
        df.rename(columns=colmap, inplace=True)
        # Construction du champ nom_prenom
        if 'nom_prenom' not in df.columns or df['nom_prenom'].isnull().any():
            df['nom_prenom'] = df['first_name'].fillna('') + ' ' + df['last_name'].fillna('')
            df['nom_prenom'] = df['nom_prenom'].str.strip()
        # Garder les colonnes utiles
        df = df[['code_utilisateur', 'nom_prenom', 'profil', 'direction']].copy()
        dfs.append(df)
    rh_all = pd.concat(dfs).drop_duplicates('code_utilisateur')
    return rh_all
''',

    "ext_utils.py": '''
import pandas as pd

def charger_et_preparer_ext(fichier_ext):
    df = pd.read_excel(fichier_ext)
    # Mapping simplifié (adapter selon besoin)
    colmap = {c: c.lower().replace(" ", "_") for c in df.columns}
    df.rename(columns=colmap, inplace=True)
    # Convert dates
    for datecol in ['last_login', 'extraction_date']:
        if datecol in df.columns:
            df[datecol] = pd.to_datetime(df[datecol], errors='coerce')
    # Normalisation des chaînes
    for txtcol in ['nom_prenom', 'profil', 'direction', 'status']:
        if txtcol in df.columns:
            df[txtcol] = df[txtcol].astype(str).str.strip().str.lower()
    return df
''',

    "match_utils.py": '''
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
    # Remplir le nom RH si vide côté extraction
    merged['nom_prenom'] = merged.apply(
        lambda row: row['nom_prenom_rh'] if (pd.isna(row['nom_prenom']) or row['nom_prenom'] == '' or row['nom_prenom'] == 'nan') else row['nom_prenom'],
        axis=1
    )
    return merged
''',

    "anomalies.py": '''
import pandas as pd

def detecter_anomalies(df):
    seuil_inactivite = 120
    df['days_inactive'] = (df['extraction_date'] - df['last_login']).dt.days
    anomalies = []
    for i, row in df.iterrows():
        tags = []
        if row['compte_non_rh']:
            tags.append("Compte non RH")
        if not row['compte_non_rh'] and row.get('profil') != row.get('profil_rh'):
            tags.append("Changement de profil à vérifier")
        if not row['compte_non_rh'] and row.get('direction') != row.get('direction_rh'):
            tags.append("Changement de direction à vérifier")
        if row['days_inactive'] and row['days_inactive'] > seuil_inactivite:
            tags.append("Compte potentiellement inactif")
        anomalies.append(", ".join(tags))
    df['anomalie'] = anomalies
    return df

def extraire_cas_a_verifier(df):
    return df[df['anomalie'].str.len() > 0]
''',

    "manual_review.py": '''
def traiter_cas_manuels(ext_df, cas_a_verifier):
    for idx, cas in cas_a_verifier.iterrows():
        print("\\n--- Cas à vérifier ---")
        print(f"Utilisateur: {cas['code_utilisateur']}")
        print(f"Nom/prénom: {cas.get('nom_prenom', '')}")
        print(f"Profil extraction: {cas.get('profil', '')} | RH: {cas.get('profil_rh', '')}")
        print(f"Direction extraction: {cas.get('direction', '')} | RH: {cas.get('direction_rh', '')}")
        print(f"Jours inactivité: {cas.get('days_inactive', '')}")
        print(f"Anomalie: {cas.get('anomalie', '')}")
        print("Actions possibles: [V]alider / [D]ésactiver / [I]gnorer / [A]utre")
        choix = input("Décision : ").strip().lower()
        if choix in ['v', 'valider']:
            decision = 'Validé'
        elif choix in ['d', 'désactiver']:
            decision = 'Désactivé'
        elif choix in ['i', 'ignorer']:
            decision = 'Ignoré'
        else:
            decision = input("Précisez votre action : ").strip()
        ext_df.loc[idx, 'decision_manuelle'] = decision
    return ext_df
''',

    "report.py": '''
import pandas as pd
from datetime import datetime

def remplir_template(template_path, ext_df, certificateur):
    rapport = ext_df.copy()
    rapport['certificateur'] = certificateur
    rapport['date_certification'] = datetime.now().strftime("%Y-%m-%d")
    cols = [
        'code_utilisateur', 'nom_prenom', 'profil', 'direction',
        'profil_rh', 'direction_rh', 'anomalie', 'decision_manuelle',
        'certificateur', 'date_certification'
    ]
    return rapport[cols]

def afficher_resume(df):
    print("\\n=== RÉSUMÉ FINAL ===")
    print(f"Comptes analysés : {len(df)}")
    print(f"Anomalies détectées : {df['anomalie'].astype(bool).sum()}")
    print(f"Décisions manuelles : {df['decision_manuelle'].notnull().sum()}")
    print(f"Comptes à désactiver : {(df['decision_manuelle'] == 'Désactivé').sum()}")
    print(f"Comptes à valider : {(df['decision_manuelle'] == 'Validé').sum()}")
''',

    "requirements.txt": '''
pandas
openpyxl
typer
pyyaml
''',
}

# Créer le dossier principal s'il n'existe pas
os.makedirs(project_root, exist_ok=True)

for filename, content in files.items():
    path = os.path.join(project_root, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ {path} créé.")

print("\nTout est prêt ! Tu peux commencer à développer Gatekeeper 🚀")
print("Active ton venv puis fais : pip install -r requirements.txt")
