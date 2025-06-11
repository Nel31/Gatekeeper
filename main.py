import typer
from core.rh_utils import charger_et_preparer_rh
from core.ext_utils import charger_et_preparer_ext
from core.match_utils import associer_rh_aux_utilisateurs
from core.anomalies import detecter_anomalies, extraire_cas_a_verifier, extraire_cas_automatiques
from core.manual_review import traiter_cas_manuels
from core.report import inject_to_template

# Mapping centralisé des décisions
DECISION_TO_LABEL = {
    "Conserver":    ("A conserver", "Conservé"),
    "Désactiver":   ("A desactiver", "Désactivé"),
    "Modifier":     ("A Modifier", "Modifié"),
}

def set_decision_columns(df):
    """Mapper les décisions vers les labels du template"""
    dec = []
    exe = []
    for v in df.get("decision_manuelle", []):
        lbl = DECISION_TO_LABEL.get(v, ("", ""))
        dec.append(lbl[0])
        exe.append(lbl[1])
    df["decision"] = dec
    df["execution_reco_decision"] = exe
    return df

app = typer.Typer()

@app.command()
def run(
    rh_files: str = typer.Option(..., help="Fichiers RH, séparés par une virgule"),
    ext_file: str = typer.Option(..., help="Fichier d'extraction applicative"),
    template_file: str = typer.Option(..., help="Template Excel"),
    output_file: str = typer.Option(..., help="Fichier de rapport à générer"),
    cert_name: str = typer.Option(..., help="Nom du certificateur"),
):
    # Chargement et préparation des données
    print("📁 Chargement des fichiers...")
    rh_paths = [p.strip() for p in rh_files.split(",")]
    rh_df = charger_et_preparer_rh(rh_paths)
    ext_df = charger_et_preparer_ext(ext_file)
    
    # Association et détection d'anomalies
    print("🔍 Détection des anomalies...")
    ext_df = associer_rh_aux_utilisateurs(ext_df, rh_df)
    ext_df = detecter_anomalies(ext_df, certificateur=cert_name)
    
    # Extraction des différents cas
    cas_a_verifier = extraire_cas_a_verifier(ext_df)
    cas_automatiques = extraire_cas_automatiques(ext_df)
    
    print(f"📊 Statistiques:")
    print(f"   - Total comptes: {len(ext_df)}")
    print(f"   - Cas automatiques: {len(cas_automatiques)}")
    print(f"   - Cas à vérifier: {len(cas_a_verifier)}")
    
    # Log des cas automatiques
    if len(cas_automatiques) > 0:
        print("\n✅ Cas traités automatiquement:")
        for _, cas in cas_automatiques.iterrows():
            print(f"   - {cas['code_utilisateur']} ({cas['nom_prenom']}): {cas['decision_manuelle']}")
    
    # Traitement manuel uniquement des cas non automatiques
    if len(cas_a_verifier) > 0:
        print("\n👤 Traitement manuel des cas restants...")
        ext_df = traiter_cas_manuels(ext_df, cas_a_verifier, certificateur=cert_name)
    else:
        print("\n✅ Aucun cas nécessitant une vérification manuelle!")

    # Préparation finale du DataFrame pour le rapport
    print("\n📄 Génération du rapport...")
    
    # S'assurer que toutes les colonnes nécessaires sont présentes
    ext_df["certificateur"] = cert_name
    ext_df["recommendation"] = "A certifier"
    ext_df = set_decision_columns(ext_df)
    
    # Vérifier que tous les comptes avec anomalies ont une décision
    anomalies_sans_decision = ext_df[(ext_df['anomalie'].str.len() > 0) & (ext_df['decision_manuelle'] == '')]
    if len(anomalies_sans_decision) > 0:
        print(f"⚠️  Attention: {len(anomalies_sans_decision)} cas sans décision!")
    
    # Injection dans le template
    inject_to_template(ext_df, template_file, output_file, certificateur=cert_name)
    
    print(f"\n✅ Rapport généré avec succès: {output_file}")
    print(f"   - Total des lignes: {len(ext_df)}")
    print(f"   - Comptes à conserver: {len(ext_df[ext_df['decision_manuelle'] == 'Conserver'])}")
    print(f"   - Comptes à modifier: {len(ext_df[ext_df['decision_manuelle'] == 'Modifier'])}")
    print(f"   - Comptes à désactiver: {len(ext_df[ext_df['decision_manuelle'] == 'Désactiver'])}")

if __name__ == "__main__":
    app()