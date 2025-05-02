# cli.py
import click
from gatekeeper.orchestrator import run_pipeline
from gatekeeper.config import settings
from gatekeeper.outlook_automation import send_via_outlook
from gatekeeper.html_generator import generate_mailto_html

@click.command()
@click.option('--rh-file', required=True, help='Path to RH Excel file')
@click.option('--ext-file', required=True, help='Path to extraction Excel file')
@click.option('--template-insgb', required=True, help='Path to In SGB report template XLSX')
@click.option('--output-insgb', required=True, help='Path for generated In SGB report XLSX')
@click.option('--certificateur', required=True, help='Name of the certificateur')
@click.option('--threshold', type=int, default=None, help='Days inactive threshold')
@click.option('--only-insgb', is_flag=True, default=False, help='Generate only In SGB report')
@click.option('--only-outsgb', is_flag=True, default=False, help='Process only Out SGB flow')
@click.option('--email-list', type=click.Path(exists=True), default=None, help='TXT file with one manager email per line')
@click.option('--use-outlook', is_flag=True, default=False, help='Use Outlook Desktop for sending')
@click.option('--generate-mailto-html', type=click.Path(), default=None, help='Generate HTML file with mailto links for Out SGB')
def main(rh_file, ext_file, template_insgb, output_insgb, certificateur,
         threshold, only_insgb, only_outsgb, email_list, use_outlook, generate_mailto_html):
    """
    - Without flags: run both In SGB report and Out SGB flow
    - --only-insgb: generate only In SGB report
    - --only-outsgb: skip In SGB, run only Out SGB flow
    """
    do_insgb = only_insgb or not only_outsgb
    do_outsgb = only_outsgb or not only_insgb

    # Override inactivity threshold if provided
    if threshold:
        settings.threshold_days_inactive = threshold

    # In SGB
    if do_insgb:
        run_pipeline(rh_file, ext_file, template_insgb, output_insgb, certificateur)
        click.echo(f"In SGB report generated at {output_insgb}")

    # Out SGB
    if do_outsgb:
        if email_list and use_outlook:
            send_via_outlook(email_list, 'outsgb', certificateur)
            click.echo("Outlook mails sent for Out SGB accounts")
        if generate_mailto_html:
            generate_mailto_html(email_list, 'outsgb', generate_mailto_html)
            click.echo(f"Generated HTML: {generate_mailto_html}")
        if not ((email_list and use_outlook) or generate_mailto_html):
            click.echo("Provide --email-list and --use-outlook or --generate-mailto-html to process Out SGB accounts.")

if __name__=='__main__':
    main()
