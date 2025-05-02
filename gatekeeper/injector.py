# gatekeeper/injector.py
from openpyxl import load_workbook
import re
from unidecode import unidecode

def normalize(text): return re.sub(r'[^a-z0-9]','',unidecode(str(text)).lower())
FIELD_TO_HEADER={
    'code_utilisateur':'Code/identifiant utilisateur','nom_prenom':'Nom et Prénom utilisateur',
    'profil':'Profil utilisateur','direction':'Direction','recommandation':'Recommandation',
    'commentaire_revue':'Commentaire revue','certificateur':'Certificateur','décision':'Décision',
    'exécution':'Exécution Reco/Décision','exécuté_par':'Exécuté par','commentaire_exécution':'Commentaire exécution'
}

def inject_to_template(report,template_path,output_path):
    wb=load_workbook(template_path)
    ws=wb.active
    hdr={normalize(c.value):c.column for c in ws[1]}
    for i,row in enumerate(report.itertuples(index=False),start=2):
        for f,v in zip(report.columns,row):
            col=hdr[normalize(FIELD_TO_HEADER[f])]
            ws.cell(row=i,column=col,value=v)
    wb.save(output_path)