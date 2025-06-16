"""
Page de génération du rapport (Étape 4)
"""

import os
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QGroupBox, QTableWidget, QTableWidgetItem,
                            QFileDialog, QHeaderView, QSizePolicy)
from PyQt6.QtGui import QFont

from ui.widgets.stat_widget import StatWidget
from ui.widgets.table_tooltip_helper import TableTooltipHelper
from ui.styles import SUCCESS_MESSAGE_STYLE, WARNING_MESSAGE_STYLE
from ui.utils import (set_decision_columns, get_last_directory, 
                     show_info_message, show_error_message, open_file_with_system)
from core.report import inject_to_template
from core.anomalies import extraire_cas_a_verifier


class ReportPage(QWidget):
    """Page de génération du rapport"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        # Permettre le redimensionnement
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setup_ui()
    
    def setup_ui(self):
        """Configurer l'interface de la page"""
        layout = QVBoxLayout(self)
        
        # Titre
        self.create_title_section(layout)
        
        # Message de confirmation
        self.create_message_section(layout)
        
        # Statistiques finales
        self.create_final_stats_section(layout)
        
        # Aperçu du rapport
        self.create_preview_section(layout)
        
        # Boutons
        self.create_buttons_section(layout)
    
    def create_title_section(self, parent_layout):
        """Créer la section titre"""
        title = QLabel("📊 Génération du rapport")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        parent_layout.addWidget(title)
    
    def create_message_section(self, parent_layout):
        """Créer la section message de confirmation"""
        self.report_message = QLabel()
        self.report_message.setStyleSheet(SUCCESS_MESSAGE_STYLE)
        self.report_message.setWordWrap(True)
        parent_layout.addWidget(self.report_message)
    
    def create_final_stats_section(self, parent_layout):
        """Créer la section des statistiques finales"""
        self.final_stats_widget = QWidget()
        self.final_stats_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        final_stats_layout = QHBoxLayout(self.final_stats_widget)
        
        self.final_stat_total = StatWidget("Total", "0", "#2196F3")
        self.final_stat_conserver = StatWidget("À conserver", "0", "#4CAF50")
        self.final_stat_modifier = StatWidget("À modifier", "0", "#FF9800")
        self.final_stat_desactiver = StatWidget("À désactiver", "0", "#F44336")
        
        final_stats_layout.addWidget(self.final_stat_total)
        final_stats_layout.addWidget(self.final_stat_conserver)
        final_stats_layout.addWidget(self.final_stat_modifier)
        final_stats_layout.addWidget(self.final_stat_desactiver)
        
        parent_layout.addWidget(self.final_stats_widget)
    
    def create_preview_section(self, parent_layout):
        """Créer la section aperçu du rapport"""
        preview_group = QGroupBox("Aperçu du rapport (100 premières lignes)")
        preview_layout = QVBoxLayout()
        
        self.report_preview = QTableWidget()
        self.report_preview.setAlternatingRowColors(True)
        self.report_preview.setSortingEnabled(True)
        preview_layout.addWidget(self.report_preview)
        
        preview_group.setLayout(preview_layout)
        parent_layout.addWidget(preview_group)
    
    def create_buttons_section(self, parent_layout):
        """Créer la section des boutons"""
        button_layout = QHBoxLayout()
        
        self.generate_button = QPushButton("📥 Télécharger le rapport Excel")
        self.generate_button.setObjectName("primaryButton")
        self.generate_button.clicked.connect(self.generate_report)
        self.generate_button.setMinimumWidth(200)
        button_layout.addWidget(self.generate_button)
        
        button_layout.addStretch()
        
        self.new_button = QPushButton("🔄 Nouvelle certification")
        self.new_button.clicked.connect(self.parent_window.reset_app)
        button_layout.addWidget(self.new_button)
        
        parent_layout.addLayout(button_layout)
    
    def update_page(self, ext_df):
        """Mettre à jour la page avec les nouvelles données"""
        self.ext_df = ext_df
        
        # Message de confirmation
        self.update_confirmation_message()
        
        # Statistiques finales
        self.update_final_statistics()
        
        # Aperçu du rapport
        self.update_report_preview()
    
    def update_confirmation_message(self):
        """Mettre à jour le message de confirmation"""
        cas_non_traites = len(extraire_cas_a_verifier(self.ext_df))
        
        if cas_non_traites == 0:
            self.report_message.setText(
                "✅ Certification terminée avec succès!\n"
                "Tous les cas ont été traités. Vous pouvez maintenant générer le rapport Excel."
            )
            self.report_message.setStyleSheet(SUCCESS_MESSAGE_STYLE)
        else:
            self.report_message.setText(
                f"⚠️ Attention: {cas_non_traites} cas n'ont pas été traités.\n"
                "Vous pouvez quand même générer le rapport, mais il sera incomplet."
            )
            self.report_message.setStyleSheet(WARNING_MESSAGE_STYLE)
    
    def update_final_statistics(self):
        """Mettre à jour les statistiques finales"""
        total = len(self.ext_df)
        conserver = len(self.ext_df[self.ext_df['decision_manuelle'] == 'Conserver'])
        modifier = len(self.ext_df[self.ext_df['decision_manuelle'] == 'Modifier'])
        desactiver = len(self.ext_df[self.ext_df['decision_manuelle'] == 'Désactiver'])
        
        # Comptes sans décision (pour diagnostic)
        sans_decision = len(self.ext_df[
            (self.ext_df['decision_manuelle'] == '') | 
            (self.ext_df['decision_manuelle'].isna())
        ])
        
        self.final_stat_total.set_value(str(total))
        self.final_stat_conserver.set_value(str(conserver))
        self.final_stat_modifier.set_value(str(modifier))
        self.final_stat_desactiver.set_value(str(desactiver))
        
        # Message de diagnostic si nécessaire
        if sans_decision > 0:
            print(f"⚠️ DIAGNOSTIC: {sans_decision} comptes sans décision détectés")
            # Ces comptes recevront automatiquement la décision "Conserver" lors de la génération
    
    def update_report_preview(self):
        """Mettre à jour l'aperçu du rapport"""
        # Préparer les données pour l'aperçu
        df_rapport = self.ext_df.copy()
        df_rapport = set_decision_columns(df_rapport, self.parent_window.certificateur)
        
        # Colonnes à afficher
        columns = ['code_utilisateur', 'nom_prenom', 'profil', 'direction', 
                  'decision', 'execution_reco_decision', 'anomalie']
        
        # Filtrer les colonnes existantes
        columns = [col for col in columns if col in df_rapport.columns]
        
        # Configurer le tableau
        self.setup_preview_table(df_rapport, columns)
        
        # Remplir le tableau
        self.fill_preview_table(df_rapport, columns)
    
    def setup_preview_table(self, df_rapport, columns):
        """Configurer le tableau d'aperçu"""
        self.report_preview.setRowCount(min(len(df_rapport), 100))
        self.report_preview.setColumnCount(len(columns))
        self.report_preview.setHorizontalHeaderLabels(columns)
    
    def fill_preview_table(self, df_rapport, columns):
        """Remplir le tableau d'aperçu"""
        for i in range(min(len(df_rapport), 100)):
            for j, col in enumerate(columns):
                value = df_rapport.iloc[i][col]
                item = QTableWidgetItem(str(value))
                self.report_preview.setItem(i, j, item)
        
        # Ajuster les colonnes
        self.report_preview.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        
        # Ajouter les tooltips automatiques
        TableTooltipHelper.setup_tooltips_for_table(self.report_preview)
    
    def generate_report(self):
        """Générer le rapport Excel"""
        # Demander où sauvegarder
        output_path = self.get_output_path()
        if not output_path:
            return
        
        try:
            # Animation du bouton
            self.set_button_processing_state(True)
            
            # Préparer et générer le rapport
            self.create_and_save_report(output_path)
            
            # Restaurer le bouton
            self.set_button_processing_state(False)
            
            # Message de succès avec option d'ouvrir
            self.show_success_message(output_path)
            
        except Exception as e:
            self.set_button_processing_state(False)
            show_error_message(
                self,
                "Erreur",
                f"Erreur lors de la génération du rapport:\n{str(e)}"
            )
    
    def get_output_path(self):
        """Demander le chemin de sauvegarde"""
        default_filename = f"rapport_certification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        default_path = os.path.join(get_last_directory(self.parent_window.settings), default_filename)
        
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer le rapport",
            default_path,
            "Fichiers Excel (*.xlsx)"
        )
        
        return output_path
    
    def create_and_save_report(self, output_path):
        """Créer et sauvegarder le rapport"""
        # Préparer les données
        df_rapport = self.ext_df.copy()
        df_rapport = set_decision_columns(df_rapport, self.parent_window.certificateur)
        
        # Générer le rapport
        inject_to_template(
            df_rapport, 
            self.parent_window.template_path, 
            output_path,
            certificateur=self.parent_window.certificateur
        )
    
    def set_button_processing_state(self, is_processing):
        """Configurer l'état du bouton selon le traitement"""
        if is_processing:
            self.generate_button.setText("⏳ Génération en cours...")
            self.generate_button.setEnabled(False)
        else:
            self.generate_button.setText("📥 Télécharger le rapport Excel")
            self.generate_button.setEnabled(True)
    
    def show_success_message(self, output_path):
        """Afficher le message de succès"""
        reply = show_info_message(
            self,
            "Rapport généré",
            f"Le rapport a été généré avec succès!\n\n{output_path}\n\nVoulez-vous l'ouvrir?"
        )
        
        if reply.name == "Open":
            open_file_with_system(output_path)
    
    def reset_page(self):
        """Réinitialiser la page"""
        self.report_message.setText("")
        self.final_stat_total.set_value("0")
        self.final_stat_conserver.set_value("0")
        self.final_stat_modifier.set_value("0")
        self.final_stat_desactiver.set_value("0")
        self.report_preview.setRowCount(0)
        self.report_preview.setColumnCount(0)