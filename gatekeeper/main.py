import click
from gatekeeper.services.orchestrator import run_pipeline

@click.command()
@click.option("--rh-file", required=True, type=click.Path(exists=True))
@click.option("--ext-file", required=True, type=click.Path(exists=True))
@click.option("--template", required=True, type=click.Path(exists=True))
@click.option("--output", required=True, type=click.Path())
def main(rh_file, ext_file, template, output):
    """
    Lance la revue Gatekeeper : RH + extractions → rapport Excel.
    """
    run_pipeline(rh_file, ext_file, template, output)

if __name__ == "__main__":
    main()
