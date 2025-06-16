from openpyxl import load_workbook
from datetime import datetime
from core.text_utils import normalize_text

FIELD_TO_HEADER = {
    'code_utilisateur':           'Code/identifiant utilisateur',
    'nom_prenom':                 'Nom et Prénom utilisateur',
    'profil':                     'Profil utilisateur',
    'direction':                  'Direction',
    'recommendation':             'Recommandation',
    'certificateur':              'Certificateur',
    'decision':                   'Décision',
    'execution_reco_decision':    'Exécution Reco/Décision',
    'comment_review':             'Commentaire revue',
    'comment_certificateur':      'Commentaire certificateur',
    'executed_by':                'Exécuté par',
    'execution_comment':          'Commentaire exécution',
    'anomalie':                   'Anomalie',
    'date_certification':         'Date certification'
}

def normalize(text: str) -> str:
    """Normaliser un texte pour la comparaison"""
    return normalize_text(text, remove_stop_words=False)

def inject_to_template(report_df, template_path: str, output_path: str, certificateur: str = ""):
    wb = load_workbook(template_path)
    ws = wb.active
    header_map = {normalize(cell.value): cell.column for cell in ws[1] if cell.value}
    date_certif = datetime.now().strftime('%Y-%m-%d')
    for i, row in enumerate(report_df.itertuples(index=False), start=2):
        for field, val in zip(report_df.columns, row):
            template_header = FIELD_TO_HEADER.get(field)
            if not template_header:
                continue
            col = header_map.get(normalize(template_header))
            if col:
                if field == 'date_certification':
                    ws.cell(row=i, column=col, value=date_certif)
                else:
                    ws.cell(row=i, column=col, value=val)
    wb.save(output_path)
    print(f"✅ Rapport généré dans {output_path}")
