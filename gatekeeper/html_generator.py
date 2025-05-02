# gatekeeper/html_generator.py
import os
from urllib.parse import quote

def generate_mailto_html(email_list_path,outsgb_dir,html_path):
    lines=['<!DOCTYPE html>','<html><body>','<h2>Envoyer certif. comptes externes</h2>','<ul>']
    for l in open(email_list_path):
        addr=l.strip()
        if not addr: continue
        file=os.path.join(outsgb_dir,f"{addr}.xlsx")
        if not os.path.exists(file): continue
        subj=quote("Validation comptes externes – à remplir")
        bod=quote("Bonjour,%0A%0AMerci de valider vos comptes externes (voir fichier).%0AIndiquez CONSERVÉ ou DÉSACTIVÉ.%0A%0ACordialement.")
        mailto=f"mailto:{addr}?subject={subj}&body={bod}"
        lines.append(f"<li><a href='{mailto}' target='_blank'>{addr}</a> → joindre {os.path.basename(file)}</li>")
    lines+=['</ul>','</body></html>']
    with open(html_path,'w',encoding='utf-8') as f: f.write("\n".join(lines))
    print(f"Generated {html_path}")
