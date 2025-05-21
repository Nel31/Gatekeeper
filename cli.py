import typer
from typing import List
from pathlib import Path
from gatekeeper.pipeline import run_pipeline
from gatekeeper.config import settings

app = typer.Typer()

@app.command()
def main(
    rh: List[Path] = typer.Option(..., help="Chemins vers les fichiers RH (.xlsx)"),
    ext: Path      = typer.Option(..., help="Chemin vers l'extraction applicative (.xlsx)"),
    template: Path = typer.Option(..., help="Chemin vers le modèle Excel de la revue (.xlsx)"),
    output: Path   = typer.Option(..., help="Chemin du rapport généré (.xlsx)"),
    cert: str      = typer.Option(..., help="Nom du certificateur"),
    threshold: int = typer.Option(None, help="Seuil d’inactivité (jours)"),
    show_comparisons: bool = typer.Option(False, help="Afficher les comparaisons de profils")
):
    """
    Lance le pipeline Gatekeeper v5 avec mapping dynamique.
    """
    if threshold:
        settings.threshold_days_inactive = threshold
    rh_paths = [str(p) for p in rh]
    run_pipeline(rh_paths, str(ext), str(template), str(output), cert, show_comparisons)
    typer.echo(f"✅ Rapport généré → {output} (certifié par {cert})")

if __name__ == "__main__":
    app()
