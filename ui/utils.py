"""
Fonctions utilitaires pour l'interface utilisateur
"""

import os
import sys
import json
from datetime import datetime
from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt

# Mapping décision -> labels (depuis main.py)
DECISION_TO_LABEL = {
    "Conserver":    ("A conserver", "Conservé"),
    "Désactiver":   ("A desactiver", "Désactivé"),
    "Modifier":     ("A Modifier", "Modifié"),
}


def set_decision_columns(df, certificateur):
    """Mapper les décisions vers les labels du template"""
    # Assurer que toutes les colonnes nécessaires existent
    df_work = ensure_required_columns(df)
    
    # Pour tous les comptes sans décision et sans anomalies : décision = "Conserver"
    mask_sans_decision = (df_work['decision_manuelle'] == "") | (df_work['decision_manuelle'].isna())
    mask_sans_anomalie = (df_work['anomalie'] == "") | (df_work['anomalie'].isna())
    
    df_work.loc[mask_sans_decision & mask_sans_anomalie, 'decision_manuelle'] = 'Conserver'
    
    # Mapper toutes les décisions vers les labels
    dec = []
    exe = []
    
    for decision in df_work['decision_manuelle']:
        lbl = DECISION_TO_LABEL.get(decision, ("", ""))
        dec.append(lbl[0])
        exe.append(lbl[1])
    
    df_work["decision"] = dec
    df_work["execution_reco_decision"] = exe
    df_work["certificateur"] = certificateur
    df_work["recommendation"] = "A certifier"
    
    return df_work


def ensure_required_columns(df):
    """S'assurer que toutes les colonnes nécessaires sont présentes"""
    df_work = df.copy()
    
    # Colonnes obligatoires avec valeurs par défaut
    required_columns = {
        'decision_manuelle': "",
        'anomalie': "",
        'cas_automatique': False,
        'comment_certificateur': "",
        'comment_review': "",
        'executed_by': "",
        'execution_comment': "",
        'date_certification': ""
    }
    
    for col, default_value in required_columns.items():
        if col not in df_work.columns:
            df_work[col] = default_value
        else:
            # Remplacer les valeurs NaN par la valeur par défaut
            df_work[col] = df_work[col].fillna(default_value)
    
    return df_work


def get_last_directory(settings):
    """Récupérer le dernier répertoire utilisé"""
    return settings.value("last_directory", os.path.expanduser("~"))


def save_last_directory(settings, file_path):
    """Sauvegarder le dernier répertoire utilisé"""
    settings.setValue("last_directory", os.path.dirname(file_path))


def save_recent_files(settings, rh_paths, ext_path, template_path, certificateur):
    """Sauvegarder les fichiers récents"""
    recent = {
        "rh_files": rh_paths,
        "ext_file": ext_path,
        "template_file": template_path,
        "certificateur": certificateur,
        "date": datetime.now().isoformat()
    }
    
    # Charger l'historique existant
    recent_list = json.loads(settings.value("recent_files", "[]"))
    recent_list.insert(0, recent)
    
    # Garder seulement les 5 derniers
    recent_list = recent_list[:5]
    
    settings.setValue("recent_files", json.dumps(recent_list))


def load_recent_files(settings):
    """Charger la liste des fichiers récents"""
    try:
        return json.loads(settings.value("recent_files", "[]"))
    except:
        return []


def open_file_with_system(file_path):
    """Ouvrir un fichier avec l'application système par défaut"""
    if sys.platform == "win32":
        os.startfile(file_path)
    elif sys.platform == "darwin":  # macOS
        os.system(f"open '{file_path}'")
    else:  # Linux
        os.system(f"xdg-open '{file_path}'")


def show_error_message(parent, title, message):
    """Afficher un message d'erreur"""
    QMessageBox.critical(parent, title, message)


def show_warning_message(parent, title, message):
    """Afficher un message d'avertissement"""
    return QMessageBox.warning(parent, title, message, 
                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                               QMessageBox.StandardButton.No)


def show_info_message(parent, title, message):
    """Afficher un message d'information"""
    return QMessageBox.information(parent, title, message,
                                   QMessageBox.StandardButton.Open | QMessageBox.StandardButton.Ok,
                                   QMessageBox.StandardButton.Ok)


def show_question_message(parent, title, message):
    """Afficher une question"""
    return QMessageBox.question(parent, title, message,
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                QMessageBox.StandardButton.No)


def show_about_dialog(parent):
    """Afficher la boîte À propos"""
    QMessageBox.about(
        parent,
        "À propos",
        """<h2>Certificateur de Comptes - Gatekeeper</h2>
        <p>Version 1.0</p>
        <p>Application de certification et d'audit des comptes utilisateurs.</p>
        <p>Cette application permet de comparer les données d'extraction 
        d'une application avec le référentiel RH pour détecter les anomalies 
        et prendre les décisions appropriées.</p>
        <p><br><i>Développé avec PyQt6 et pandas</i></p>"""
    )


def show_documentation_dialog(parent):
    """Afficher la documentation"""
    doc_text = """
<h2>Guide d'utilisation du Certificateur de Comptes</h2>

<h3>🚀 Démarrage rapide</h3>
<ol>
<li><b>Renseignez votre nom</b> dans le champ "Certificateur"</li>
<li><b>Sélectionnez les fichiers RH</b> (un ou plusieurs fichiers Excel)</li>
<li><b>Sélectionnez le fichier d'extraction</b> depuis l'application à auditer</li>
<li><b>Sélectionnez le template</b> pour la génération du rapport</li>
<li><b>Lancez le traitement</b> et suivez les étapes</li>
</ol>

<h3>📋 Format des fichiers</h3>
<p><b>Fichiers RH:</b> Doivent contenir au minimum les colonnes code_utilisateur, nom_prenom, profil, direction</p>
<p><b>Fichier d'extraction:</b> Export de l'application avec les mêmes colonnes</p>
<p><b>Template:</b> Modèle Excel avec les en-têtes pour le rapport final</p>

<h3>🔍 Types d'anomalies détectées</h3>
<ul>
<li><b>Compte non RH:</b> Utilisateur présent dans l'application mais absent du référentiel RH</li>
<li><b>Changement de profil:</b> Différence entre le profil dans l'application et celui du RH</li>
<li><b>Changement de direction:</b> Différence entre la direction dans l'application et celle du RH</li>
<li><b>Compte inactif:</b> Compte sans connexion depuis plus de 120 jours</li>
</ul>

<h3>✅ Actions possibles</h3>
<ul>
<li><b>Modifier:</b> Mettre à jour selon les données RH</li>
<li><b>Conserver:</b> Tolérer l'écart et l'ajouter à la whitelist</li>
<li><b>Désactiver:</b> Supprimer ou suspendre le compte</li>
</ul>

<h3>💡 Astuces</h3>
<ul>
<li>Les fichiers récents sont accessibles via le menu Fichier</li>
<li>La whitelist est automatiquement mise à jour lors des validations</li>
<li>Vous pouvez ajouter des commentaires pour justifier vos décisions</li>
<li>Le rapport peut être généré même si tous les cas n'ont pas été traités</li>
</ul>
    """
    
    msg = QMessageBox(parent)
    msg.setWindowTitle("Documentation")
    msg.setTextFormat(Qt.TextFormat.RichText)
    msg.setText(doc_text)
    msg.setIcon(QMessageBox.Icon.Information)
    msg.exec()


def show_decision_help_dialog(parent):
    """Afficher l'aide pour les décisions"""
    help_text = """
<h3>💡 Guide des décisions</h3>

<h4>🔧 Modifier</h4>
<p>Utilisez cette option quand :</p>
<ul>
<li>Le profil/direction RH est plus à jour que celui de l'application</li>
<li>L'utilisateur a changé de poste récemment</li>
<li>C'est une erreur de saisie dans l'application</li>
</ul>

<h4>✅ Conserver</h4>
<p>Utilisez cette option quand :</p>
<ul>
<li>L'écart est justifié et acceptable</li>
<li>C'est un cas particulier validé</li>
<li>Le compte nécessite des droits spéciaux</li>
</ul>

<h4>❌ Désactiver</h4>
<p>Utilisez cette option quand :</p>
<ul>
<li>L'utilisateur a quitté l'entreprise</li>
<li>Le compte est inactif depuis longtemps (>120 jours)</li>
<li>C'est un compte de test ou temporaire</li>
<li>Aucune justification valable pour l'écart</li>
</ul>

<p><b>Note:</b> Les décisions "Conserver" et "Modifier" ajoutent automatiquement 
les cas à la whitelist pour les prochaines certifications.</p>
    """
    
    msg = QMessageBox(parent)
    msg.setWindowTitle("Aide aux décisions")
    msg.setTextFormat(Qt.TextFormat.RichText)
    msg.setText(help_text)
    msg.setIcon(QMessageBox.Icon.Information)
    msg.exec()


def format_file_size(size_bytes):
    """Formatter la taille d'un fichier"""
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024.0 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"