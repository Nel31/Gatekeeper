# cli.py
import click
from gatekeeper.orchestrator import run_pipeline
from gatekeeper.config import settings

@click.command()
@click.option('--rh-file', required=True, help='Fichier RH .xlsx')
@click.option('--ext-file', required=True, help='Fichier extraction .xlsx')
@click.option('--template', required=True, help='Template report .xlsx')
@click.option('--output', required=True, help='Chemin du rapport généré')
@click.option('--certificateur', required=True, help='Nom du certificateur')
@click.option('--threshold', type=int, default=None,
              help='Seuil inactivité en jours')
def main(rh_file, ext_file, template, output,
         certificateur, threshold):
    if threshold:
        settings.threshold_days_inactive = threshold

    run_pipeline(
        rh_file, ext_file, template,
        output, certificateur
    )
    click.echo(
        f"Report generated at {output} by {certificateur}"
    )

if __name__ == '__main__':
    main()
