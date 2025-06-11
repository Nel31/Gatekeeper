"""
Page de validation manuelle (Étape 3)
"""

import pandas as pd
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QGroupBox, QRadioButton, QTextEdit, 
                            QProgressBar)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from ui.styles import RADIO_BUTTON_STYLE
from core.anomalies import extraire_cas_a_verifier
from mapping.profils_valides import ajouter_profil_valide
from mapping.directions_conservees import ajouter_direction_conservee


class ValidationPage(QWidget):
    """Page de validation manuelle"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.current_cas_index = 0
        self.setup_ui()
    
    def setup_ui(self):
        """Configurer l'interface de la page"""
        layout = QVBoxLayout(self)
        
        # Titre avec compteur
        self.create_title_section(layout)
        
        # Progression
        self.create_progress_section(layout)
        
        # Conteneur principal avec deux colonnes
        self.create_content_section(layout)
        
        # Bouton pour terminer
        self.create_finish_button(layout)
    
    def create_title_section(self, parent_layout):
        """Créer la section titre"""
        title_layout = QHBoxLayout()
        title = QLabel("✅ Validation manuelle")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_layout.addWidget(title)
        
        title_layout.addStretch()
        
        self.validation_counter = QLabel()
        self.validation_counter.setStyleSheet("font-size: 16px; color: #1976d2; font-weight: bold;")
        title_layout.addWidget(self.validation_counter)
        
        parent_layout.addLayout(title_layout)
    
    def create_progress_section(self, parent_layout):
        """Créer la section de progression"""
        self.validation_progress = QProgressBar()
        self.validation_progress.setTextVisible(True)
        parent_layout.addWidget(self.validation_progress)
    
    def create_content_section(self, parent_layout):
        """Créer la section de contenu principal"""
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        
        # Colonne gauche: Détails
        self.create_details_column(content_layout)
        
        # Colonne droite: Actions
        self.create_actions_column(content_layout)
        
        parent_layout.addWidget(content_widget)
    
    def create_details_column(self, parent_layout):
        """Créer la colonne des détails"""
        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)
        
        # Détails du cas
        self.cas_details = QGroupBox("Détails du cas")
        cas_layout = QVBoxLayout()
        
        self.cas_info_label = QLabel()
        self.cas_info_label.setStyleSheet("font-size: 13px; line-height: 1.6;")
        cas_layout.addWidget(self.cas_info_label)
        
        self.cas_details.setLayout(cas_layout)
        left_layout.addWidget(self.cas_details)
        
        # Comparaison visuelle
        self.comparison_group = QGroupBox("Comparaison Extraction vs RH")
        comparison_layout = QVBoxLayout()
        
        self.comparison_label = QLabel()
        comparison_layout.addWidget(self.comparison_label)
        
        self.comparison_group.setLayout(comparison_layout)
        left_layout.addWidget(self.comparison_group)
        
        parent_layout.addWidget(left_column, 2)
    
    def create_actions_column(self, parent_layout):
        """Créer la colonne des actions"""
        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)
        
        # Actions possibles
        self.create_actions_group(right_layout)
        
        # Boutons d'action
        self.create_action_buttons(right_layout)
        
        parent_layout.addWidget(right_column, 1)
    
    def create_actions_group(self, parent_layout):
        """Créer le groupe des actions possibles"""
        self.actions_group = QGroupBox("Actions possibles")
        actions_layout = QVBoxLayout()
        
        self.radio_modifier = QRadioButton("✏️ Modifier - Mettre à jour selon le RH")
        self.radio_conserver = QRadioButton("✓ Conserver - Tolérer l'écart")
        self.radio_desactiver = QRadioButton("❌ Désactiver - Supprimer le compte")
        
        # Style pour les radio buttons
        self.radio_modifier.setStyleSheet(RADIO_BUTTON_STYLE)
        self.radio_conserver.setStyleSheet(RADIO_BUTTON_STYLE)
        self.radio_desactiver.setStyleSheet(RADIO_BUTTON_STYLE)
        
        actions_layout.addWidget(self.radio_modifier)
        actions_layout.addWidget(self.radio_conserver)
        actions_layout.addWidget(self.radio_desactiver)
        
        # Commentaire
        comment_label = QLabel("Commentaire (optionnel):")
        comment_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        actions_layout.addWidget(comment_label)
        
        self.comment_edit = QTextEdit()
        self.comment_edit.setPlaceholderText("Ajoutez un commentaire pour justifier votre décision...")
        self.comment_edit.setMaximumHeight(100)
        actions_layout.addWidget(self.comment_edit)
        
        self.actions_group.setLayout(actions_layout)
        parent_layout.addWidget(self.actions_group)
    
    def create_action_buttons(self, parent_layout):
        """Créer les boutons d'action"""
        action_buttons_layout = QHBoxLayout()
        
        self.back_to_table_button = QPushButton("← Retour au tableau")
        self.back_to_table_button.clicked.connect(lambda: self.parent_window.go_to_step(1))
        self.back_to_table_button.setToolTip("Retourner au tableau pour prendre les décisions directement")
        action_buttons_layout.addWidget(self.back_to_table_button)
        
        action_buttons_layout.addStretch()
        
        self.skip_button = QPushButton("⏭️ Passer ce cas")
        self.skip_button.clicked.connect(self.skip_case)
        action_buttons_layout.addWidget(self.skip_button)
        
        self.validate_button = QPushButton("✅ Valider")
        self.validate_button.setObjectName("successButton")
        self.validate_button.clicked.connect(self.validate_decision)
        self.validate_button.setMinimumWidth(120)
        action_buttons_layout.addWidget(self.validate_button)
        
        parent_layout.addLayout(action_buttons_layout)
    
    def create_finish_button(self, parent_layout):
        """Créer le bouton de fin de validation"""
        finish_layout = QHBoxLayout()
        finish_layout.addStretch()
        
        self.finish_validation_button = QPushButton("Terminer la validation →")
        self.finish_validation_button.setObjectName("primaryButton")
        self.finish_validation_button.clicked.connect(lambda: self.parent_window.go_to_step(3))
        self.finish_validation_button.setVisible(False)
        self.finish_validation_button.setMinimumWidth(200)
        finish_layout.addWidget(self.finish_validation_button)
        
        finish_layout.addStretch()
        parent_layout.addLayout(finish_layout)
    
    def show_current_case(self, ext_df):
        """Afficher le cas en cours de validation"""
        self.ext_df = ext_df
        
        # Mettre à jour la liste des cas à vérifier
        self.cas_a_verifier = extraire_cas_a_verifier(ext_df)
        
        if len(self.cas_a_verifier) == 0:
            self.show_completion_message()
            return
        
        # Réinitialiser l'index si nécessaire
        if self.current_cas_index >= len(self.cas_a_verifier):
            self.current_cas_index = 0
        
        # Afficher le cas
        self.display_case()
    
    def show_completion_message(self):
        """Afficher le message de fin de validation"""
        self.validation_counter.setText("✅ Tous les cas traités")
        self.cas_info_label.setText("Tous les cas ont été traités!")
        self.comparison_group.setVisible(False)
        self.actions_group.setEnabled(False)
        self.validate_button.setVisible(False)
        self.skip_button.setVisible(False)
        self.finish_validation_button.setVisible(True)
        
        # Message informatif avec récapitulatif
        info_text = self.create_completion_info_text()
        self.cas_info_label.setText(info_text)
    
    def create_completion_info_text(self):
        """Créer le texte informatif de fin de validation"""
        conserver_count = len(self.ext_df[self.ext_df['decision_manuelle'] == 'Conserver'])
        modifier_count = len(self.ext_df[self.ext_df['decision_manuelle'] == 'Modifier'])
        desactiver_count = len(self.ext_df[self.ext_df['decision_manuelle'] == 'Désactiver'])
        
        return f"""
<p style="font-size: 14px; color: #4caf50;">
<b>✅ Excellente nouvelle !</b><br><br>
Tous les cas ont été traités avec succès.<br>
Vous pouvez maintenant générer le rapport final.
</p>
<p style="margin-top: 20px;">
<b>Récapitulatif des décisions :</b><br>
• Comptes à conserver : {conserver_count}<br>
• Comptes à modifier : {modifier_count}<br>
• Comptes à désactiver : {desactiver_count}<br>
</p>
        """
    
    def display_case(self):
        """Afficher les informations du cas actuel"""
        # Compteur
        self.validation_counter.setText(f"Cas {self.current_cas_index + 1} sur {len(self.cas_a_verifier)}")
        
        # Récupérer le cas actuel
        cas_idx = self.cas_a_verifier.index[self.current_cas_index]
        cas = self.cas_a_verifier.loc[cas_idx]
        
        # Afficher les informations de base
        self.display_case_info(cas)
        
        # Comparaison visuelle
        self.display_comparison(cas)
        
        # Configurer les actions selon l'anomalie
        self.configure_actions(cas)
        
        # Réinitialiser le commentaire
        self.comment_edit.clear()
        
        # Mise à jour de la progression
        self.update_progress()
    
    def display_case_info(self, cas):
        """Afficher les informations du cas"""
        try:
            jours = cas.get('days_inactive', '')
            if isinstance(jours, (int, float)) and not pd.isna(jours):
                jours_affiche = f"{jours:.0f}"
            else:
                jours_affiche = "Non renseigné"
        except:
            jours_affiche = "Non renseigné"
        
        info_text = f"""
<p><b>Utilisateur:</b> {cas.get('code_utilisateur', 'N/A')}</p>
<p><b>Nom/Prénom:</b> {cas.get('nom_prenom', 'N/A')}</p>
<p><b>Jours d'inactivité:</b> {jours_affiche}</p>
<p style="margin-top: 10px;"><b style="color: #ff9800;">⚠️ Anomalie détectée:</b><br>{cas.get('anomalie', 'N/A')}</p>
        """
        
        self.cas_info_label.setText(info_text)
    
    def display_comparison(self, cas):
        """Afficher la comparaison extraction vs RH"""
        comparison_text = f"""
<table style="width: 100%; border-collapse: collapse;">
<tr>
    <th style="text-align: left; padding: 8px; background-color: #f5f5f5;">Champ</th>
    <th style="text-align: left; padding: 8px; background-color: #f5f5f5;">Extraction</th>
    <th style="text-align: left; padding: 8px; background-color: #f5f5f5;">RH</th>
</tr>
<tr>
    <td style="padding: 8px; border-top: 1px solid #ddd;"><b>Profil</b></td>
    <td style="padding: 8px; border-top: 1px solid #ddd;">{cas.get('profil', 'N/A')}</td>
    <td style="padding: 8px; border-top: 1px solid #ddd; background-color: #e3f2fd;">{cas.get('profil_rh', 'N/A')}</td>
</tr>
<tr>
    <td style="padding: 8px; border-top: 1px solid #ddd;"><b>Direction</b></td>
    <td style="padding: 8px; border-top: 1px solid #ddd;">{cas.get('direction', 'N/A')}</td>
    <td style="padding: 8px; border-top: 1px solid #ddd; background-color: #e3f2fd;">{cas.get('direction_rh', 'N/A')}</td>
</tr>
</table>
        """
        
        self.comparison_label.setText(comparison_text)
        self.comparison_group.setVisible(True)
    
    def configure_actions(self, cas):
        """Configurer les actions selon l'anomalie"""
        anomalie = cas.get('anomalie', '')
        
        if "Changement de profil à vérifier" in anomalie or "Changement de direction à vérifier" in anomalie:
            self.radio_modifier.setVisible(True)
            self.radio_modifier.setChecked(True)
        else:
            self.radio_modifier.setVisible(False)
            self.radio_conserver.setChecked(True)
    
    def update_progress(self):
        """Mettre à jour la barre de progression"""
        if len(self.cas_a_verifier) > 0:
            progress = self.current_cas_index / len(self.cas_a_verifier) * 100
            self.validation_progress.setValue(int(progress))
            self.validation_progress.setFormat(f"{int(progress)}% - {self.current_cas_index}/{len(self.cas_a_verifier)} cas traités")
        else:
            self.validation_progress.setValue(100)
            self.validation_progress.setFormat("100% - Terminé")
    
    def validate_decision(self):
        """Valider la décision pour le cas en cours"""
        if len(self.cas_a_verifier) == 0:
            return
        
        # Récupérer la décision
        decision = self.get_selected_decision()
        
        # Récupérer le cas actuel
        cas_idx = self.cas_a_verifier.index[self.current_cas_index]
        cas = self.cas_a_verifier.loc[cas_idx]
        
        # Enregistrer la décision
        self.save_decision(cas_idx, decision, cas)
        
        # Message de confirmation
        self.parent_window.show_status_message(f"✅ Décision '{decision}' enregistrée", 2000)
        
        # Passer au cas suivant ou terminer
        self.proceed_to_next_case()
    
    def get_selected_decision(self):
        """Récupérer la décision sélectionnée"""
        if self.radio_modifier.isChecked():
            return "Modifier"
        elif self.radio_conserver.isChecked():
            return "Conserver"
        elif self.radio_desactiver.isChecked():
            return "Désactiver"
        return ""
    
    def save_decision(self, cas_idx, decision, cas):
        """Sauvegarder la décision et le commentaire"""
        # Enregistrer la décision
        self.ext_df.loc[cas_idx, 'decision_manuelle'] = decision
        
        # Enregistrer le commentaire si présent
        comment = self.comment_edit.toPlainText().strip()
        if comment:
            self.ext_df.loc[cas_idx, 'comment_certificateur'] = comment
        
        # Ajouter aux whitelists si nécessaire
        if decision in ["Modifier", "Conserver"]:
            self.add_to_whitelists(cas, decision)
    
    def add_to_whitelists(self, cas, decision):
        """Ajouter aux whitelists si nécessaire"""
        anomalie = cas.get('anomalie', '')
        if "Changement de profil à vérifier" in anomalie:
            ajouter_profil_valide(cas, certificateur=self.parent_window.certificateur)
        if "Changement de direction à vérifier" in anomalie:
            ajouter_direction_conservee(cas, certificateur=self.parent_window.certificateur)
    
    def proceed_to_next_case(self):
        """Passer au cas suivant ou afficher la fin"""
        # Mettre à jour les cas à vérifier
        self.cas_a_verifier = extraire_cas_a_verifier(self.ext_df)
        
        if len(self.cas_a_verifier) > 0:
            self.current_cas_index = 0  # Réinitialiser l'index
            self.display_case()
        else:
            self.show_completion_message()
    
    def skip_case(self):
        """Passer au cas suivant sans décision"""
        self.current_cas_index += 1
        if self.current_cas_index >= len(self.cas_a_verifier):
            self.current_cas_index = 0
        self.display_case()
    
    def reset_page(self):
        """Réinitialiser la page"""
        self.current_cas_index = 0
        self.validation_counter.setText("")
        self.cas_info_label.setText("")
        self.comparison_label.setText("")
        self.comparison_group.setVisible(True)
        self.actions_group.setEnabled(True)
        self.validate_button.setVisible(True)
        self.skip_button.setVisible(True)
        self.finish_validation_button.setVisible(False)
        self.comment_edit.clear()
        self.validation_progress.setValue(0)