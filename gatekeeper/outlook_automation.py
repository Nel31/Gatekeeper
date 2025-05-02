# gatekeeper/outlook_automation.py
import csv,datetime
import win32com.client
from pathlib import Path

LOG_FILE='outlook_send_log.csv'

def send_via_outlook(email_list_path,outsgb_dir,certificateur):
    addrs=[l.strip() for l in open(email_list_path) if l.strip()]
    outlook=win32com.client.Dispatch('Outlook.Application')
    subject=f"Validation comptes externes – {certificateur}"
    body=("Bonjour,\n\nVous trouverez en pièce jointe le fichier Excel pour certifier vos comptes externes.\n\nMerci d’indiquer CONSERVÉ ou DÉSACTIVÉ pour chaque compte.\n\n"+f"Cordialement,\n{certificateur}")
    if not Path(LOG_FILE).exists():
        with open(LOG_FILE,'w',newline='') as f: csv.writer(f).writerow(['timestamp','address','status','error'])
    for addr in addrs:
        mail=outlook.CreateItem(0)
        mail.To=addr; mail.Subject=subject; mail.Body=body
        fp=Path(outsgb_dir)/f"{addr}.xlsx"
        if fp.exists(): mail.Attachments.Add(str(fp))
        else: _log(addr,'Échec',f'Missing {fp.name}'); continue
        try: mail.Send(); _log(addr,'Succès','')
        except Exception as e: _log(addr,'Échec',str(e))

def _log(addr,status,error):
    ts=datetime.datetime.now().isoformat()
    with open(LOG_FILE,'a',newline='') as f: csv.writer(f).writerow([ts,addr,status,error])
    print(f"[{ts}] {addr} → {status}{' ('+error+')' if error else ''}")