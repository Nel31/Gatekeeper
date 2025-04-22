import pytest
from scripts.report_generator import generate_report
import pandas as pd
import os

def test_generate_report(tmp_path):
    # Create a minimal template and DataFrame, then generate report
    template = tmp_path / "template.xlsx"
    # create a template with headers
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    headers = ["code/Identifiant utilisateur", "Utilisateur", "Profil utilisateur",
               "Direction", "Recommandation", "Commentaire Revue",
               "Certificateur", "Décision", "Commentaire Certificateur",
               "Exécution Décision", "Exécuté par", "Commentaire Exécution"]
    ws.append(headers)
    wb.save(template)
    df = pd.DataFrame([["U1", "Test User", "Profile", "", "", "", "", "", "", "", "", ""]], columns=headers)
    output = tmp_path / "output.xlsx"
    generate_report(df, str(template), str(output))
    assert os.path.exists(output)
