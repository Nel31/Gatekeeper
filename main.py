import typer
from rh_utils import charger_et_preparer_rh
from ext_utils import charger_et_preparer_ext
from match_utils import associer_rh_aux_utilisateurs
from anomalies import detecter_anomalies, extraire_cas_a_verifier
from manual_review import traiter_cas_manuels
from report import inject_to_template

DECISION_TO_LABEL = {
    "Conserver":    ("A conserver", "Conservé"),
    "Désactiver":   ("A desactiver", "Désactivé"),
    "Modifier":     ("A Modifier", "Modifié"),
}

def set_decision_columns(df):
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
    rh_paths = [p.strip() for p in rh_files.split(",")]
    rh_df = charger_et_preparer_rh(rh_paths)
    ext_df = charger_et_preparer_ext(ext_file)
    ext_df = associer_rh_aux_utilisateurs(ext_df, rh_df)
    ext_df = detecter_anomalies(ext_df, certificateur=cert_name)
    cas_a_verifier = extraire_cas_a_verifier(ext_df)
    ext_df = traiter_cas_manuels(ext_df, cas_a_verifier, certificateur=cert_name)

    # Règles métiers finales
    ext_df["certificateur"] = cert_name
    ext_df["recommendation"] = "A certifier"
    ext_df = set_decision_columns(ext_df)

    inject_to_template(ext_df, template_file, output_file, certificateur=cert_name)

if __name__ == "__main__":
    app()
