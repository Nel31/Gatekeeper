"""
Fenêtre principale de l'application Certificateur
"""

import os
import json
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QStackedWidget, QMenuBar, QMenu, 
                            QMessageBox, QSizePolicy, QDialog)
from PyQt6.QtCore import Qt, QTimer, QSettings
from PyQt6.QtGui import QAction, QFont

from ui.styles import (MAIN_STYLE, STEP_ACTIVE_STYLE, STEP_COMPLETED_STYLE, 
                      STEP_INACTIVE_STYLE, STEP_TEXT_ACTIVE_STYLE, 
                      STEP_TEXT_COMPLETED_STYLE, STEP_TEXT_INACTIVE_STYLE)
from ui.pages.loading_page import LoadingPage
from ui.pages.anomalies_page import AnomaliesPage
from ui.pages.validation_page import ValidationPage
from ui.pages.report_page import ReportPage
from ui.threads.processing_thread import ProcessingThread
from ui.utils import (save_recent_files, load_recent_files, show_about_dialog,
                     show_documentation_dialog, show_question_message, 
                     show_error_message)
from ui.dialogs.clear_data_dialog import ClearDataDialog
from resource_path import persistent_data_path


class CertificateurApp(QMainWindow):
    """Fenêtre principale de l'application Certificateur"""
    
    def __init__(self):
        super().__init__()
        self.setup_window()
        self.setup_variables()
        self.setup_ui()
        self.load_recent_files_menu()
    
    def setup_window(self):
        """Configurer la fenêtre principale"""
        self.setWindowTitle("Certificateur de Comptes - Gatekeeper")
        # Définir une taille minimale raisonnable
        self.setMinimumSize(1000, 800)
        # Permettre le redimensionnement
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet(MAIN_STYLE)
    
    def setup_variables(self):
        """Initialiser les variables d'état"""
        self.ext_df = None
        self.certificateur = ""
        self.rh_paths = []
        self.ext_path = ""
        self.template_path = ""
        
        # Settings pour persistance
        self.settings = QSettings("Gatekeeper", "Certificateur")
        
        # Timer pour les messages temporaires
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(lambda: self.status_label.setText("Prêt"))
    
    def setup_ui(self):
        """Configurer l'interface utilisateur"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        
        # Menu bar
        self.create_menu_bar()
        
        # Barre de navigation
        self.create_navigation_bar(main_layout)
        
        # Stack pour les différentes étapes
        self.create_pages_stack(main_layout)
        
        # Barre de statut
        self.create_status_bar()

    def show_clear_data_dialog(self):
        """Afficher la boîte de dialogue pour effacer les données"""
        dialog = ClearDataDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_items = dialog.get_selected_items()
            if selected_items:
                self.confirm_and_clear_data(selected_items)
        
    def create_menu_bar(self):
        """Créer la barre de menu"""
        menubar = self.menuBar()
        
        # Menu Fichier
        self.create_file_menu(menubar)
        
        # Menu Aide
        self.create_help_menu(menubar)
    
    def confirm_and_clear_data(self, items):
        """Confirmer et effacer les données sélectionnées"""
        # Construire le message de confirmation
        items_text = "\n".join([f"• {item}" for item in items])
        
        reply = QMessageBox.warning(
            self,
            "Confirmation de suppression",
            f"Vous êtes sur le point d'effacer définitivement :\n\n{items_text}\n\n"
            "Cette action est irréversible. Voulez-vous continuer ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.clear_selected_data(items)
            QMessageBox.information(
                self,
                "Données effacées",
                "Les données sélectionnées ont été effacées avec succès."
            )

    def clear_selected_data(self, items):
        """Effacer les données sélectionnées"""
        import os
        
        if "Historique des fichiers récents" in items:
            self.settings.remove("recent_files")
            self.update_recent_menu()
        
        if "Profils validés (whitelist)" in items:
            files = ["profils_valides.csv", "variations_profils.csv", "changements_profils.csv"]
            for f in files:
                path = persistent_data_path(f)
                if os.path.exists(path):
                    os.remove(path)
        
        if "Directions conservées" in items:
            files = ["directions_conservees.csv", "variations_directions.csv", "changements_directions.csv"]
            for f in files:
                path = persistent_data_path(f)
                if os.path.exists(path):
                    os.remove(path)
        
        if "Variations d'écriture" in items:
            files = ["variations_profils.csv", "variations_directions.csv"]
            for f in files:
                path = persistent_data_path(f)
                if os.path.exists(path):
                    os.remove(path)
    
    def create_file_menu(self, menubar):
        """Créer le menu Fichier"""
        file_menu = menubar.addMenu('Fichier')
        
        # Nouvelle certification
        new_action = QAction('Nouvelle certification', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.reset_app)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        # Fichiers récents
        self.recent_menu = file_menu.addMenu('Fichiers récents')
        
        file_menu.addSeparator()
        
        # Effacer les données mémorisées
        clear_data_action = QAction('Effacer les données mémorisées...', self)
        clear_data_action.triggered.connect(self.show_clear_data_dialog)
        file_menu.addAction(clear_data_action)
        
        file_menu.addSeparator()
        
        # Quitter
        quit_action = QAction('Quitter', self)
        quit_action.setShortcut('Ctrl+Q')
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

    def create_help_menu(self, menubar):
        """Créer le menu Aide"""
        help_menu = menubar.addMenu('Aide')
        
        # Documentation
        doc_action = QAction('Documentation', self)
        doc_action.setShortcut('F1')
        doc_action.triggered.connect(lambda: show_documentation_dialog(self))
        help_menu.addAction(doc_action)
        
        # À propos
        about_action = QAction('À propos', self)
        about_action.triggered.connect(lambda: show_about_dialog(self))
        help_menu.addAction(about_action)
    
    def create_navigation_bar(self, parent_layout):
        """Créer la barre de navigation avec les étapes"""
        nav_widget = QWidget()
        nav_widget.setFixedHeight(80)
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setSpacing(20)
        
        self.step_labels = []
        steps = ["📁 Chargement", "🔍 Anomalies", "✅ Validation", "📊 Rapport"]
        
        for i, step in enumerate(steps):
            step_widget = self.create_step_widget(i + 1, step)
            nav_layout.addWidget(step_widget)
            
            if i < len(steps) - 1:
                arrow = QLabel("→")
                arrow.setStyleSheet("color: #ccc; font-size: 20px;")
                arrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
                nav_layout.addWidget(arrow)
        
        parent_layout.addWidget(nav_widget)
        self.update_navigation(0)
    
    def create_step_widget(self, number, label):
        """Créer un widget d'étape de navigation"""
        step_widget = QWidget()
        step_layout = QVBoxLayout(step_widget)
        step_layout.setSpacing(5)
        
        # Numéro de l'étape
        number_label = QLabel(str(number))
        number_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        number_label.setFixedSize(30, 30)
        number_label.setStyleSheet(STEP_INACTIVE_STYLE)
        
        # Nom de l'étape
        text_label = QLabel(label)
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setStyleSheet(STEP_TEXT_INACTIVE_STYLE)
        
        step_layout.addWidget(number_label, alignment=Qt.AlignmentFlag.AlignCenter)
        step_layout.addWidget(text_label)
        
        self.step_labels.append((number_label, text_label))
        return step_widget
    
    def create_pages_stack(self, parent_layout):
        """Créer le stack des pages"""
        self.stack = QStackedWidget()
        
        # Créer les pages
        self.loading_page = LoadingPage(self)
        self.anomalies_page = AnomaliesPage(self)
        self.validation_page = ValidationPage(self)
        self.report_page = ReportPage(self)
        
        # Connecter le signal back_clicked de la page anomalies
        self.anomalies_page.back_clicked.connect(lambda: self.go_to_step(0))
        
        # Ajouter au stack
        self.stack.addWidget(self.loading_page)
        self.stack.addWidget(self.anomalies_page)
        self.stack.addWidget(self.validation_page)
        self.stack.addWidget(self.report_page)
        
        parent_layout.addWidget(self.stack)
    
    def create_status_bar(self):
        """Créer la barre de statut"""
        self.status_label = QLabel("Prêt")
        self.statusBar().addPermanentWidget(self.status_label)
    
    def update_navigation(self, current_step):
        """Mettre à jour l'apparence de la barre de navigation"""
        for i, (number_label, text_label) in enumerate(self.step_labels):
            if i == current_step:
                number_label.setStyleSheet(STEP_ACTIVE_STYLE)
                text_label.setStyleSheet(STEP_TEXT_ACTIVE_STYLE)
            elif i < current_step:
                number_label.setStyleSheet(STEP_COMPLETED_STYLE)
                text_label.setStyleSheet(STEP_TEXT_COMPLETED_STYLE)
            else:
                number_label.setStyleSheet(STEP_INACTIVE_STYLE)
                text_label.setStyleSheet(STEP_TEXT_INACTIVE_STYLE)
    
    def go_to_step(self, step):
        """Naviguer vers une étape"""
        self.stack.setCurrentIndex(step)
        self.update_navigation(step)
        
        if step == 2:
            self.validation_page.show_current_case(self.ext_df)
        elif step == 3:
            self.report_page.update_page(self.ext_df)
    
    def process_data(self):
        """Lancer le traitement des données"""
        self.certificateur = self.loading_page.get_certificateur()
        
        # Animation du bouton
        self.loading_page.process_button.setText("⏳ Traitement en cours...")
        self.loading_page.process_button.setEnabled(False)
        
        # Afficher la progression
        self.loading_page.progress_bar.setVisible(True)
        self.loading_page.progress_label.setVisible(True)
        self.loading_page.progress_bar.setRange(0, 0)  # Mode indéterminé
        
        # Créer et lancer le thread
        self.processing_thread = ProcessingThread(
            self.rh_paths, 
            self.ext_path, 
            self.certificateur
        )
        self.processing_thread.progress.connect(self.update_progress)
        self.processing_thread.finished.connect(self.processing_finished)
        self.processing_thread.error.connect(self.processing_error)
        self.processing_thread.start()
    
    def update_progress(self, message):
        """Mettre à jour le message de progression"""
        self.loading_page.progress_label.setText(message)
        self.show_status_message(message, 0)
    
    def processing_finished(self, ext_df):
        """Traitement terminé avec succès"""
        self.ext_df = ext_df
        
        # Masquer la progression
        self.loading_page.progress_bar.setVisible(False)
        self.loading_page.progress_label.setVisible(False)
        
        # Restaurer le bouton
        self.loading_page.process_button.setText("🚀 Lancer le traitement")
        
        # Message de succès
        self.show_status_message("✅ Traitement terminé avec succès!", 3000)
        
        # Sauvegarder comme fichiers récents
        self.save_current_session()
        
        # Mettre à jour la page des anomalies
        self.anomalies_page.update_page(ext_df)
        
        # Passer à la page suivante
        self.go_to_step(1)
    
    def processing_error(self, error_message):
        """Erreur lors du traitement"""
        self.loading_page.progress_bar.setVisible(False)
        self.loading_page.progress_label.setVisible(False)
        self.loading_page.process_button.setText("🚀 Lancer le traitement")
        self.loading_page.process_button.setEnabled(True)
        
        show_error_message(
            self, 
            "Erreur", 
            f"Erreur lors du traitement:\n\n{error_message}\n\nVérifiez que les fichiers sont au bon format."
        )
    
    def reset_app(self, ask_confirmation=True):
        """Réinitialiser l'application"""
        if ask_confirmation:
            reply = show_question_message(
                self,
                "Nouvelle certification",
                "Voulez-vous vraiment recommencer une nouvelle certification?\n\nToutes les données non sauvegardées seront perdues."
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # Réinitialiser toutes les variables
        self.ext_df = None
        self.certificateur = ""
        self.rh_paths = []
        self.ext_path = ""
        self.template_path = ""
        
        # Réinitialiser les pages
        self.loading_page.reset_form()
        self.anomalies_page.reset_page()
        self.validation_page.reset_page()
        self.report_page.reset_page()
        
        # Retourner à la première page
        self.go_to_step(0)
        
        self.show_status_message("Application réinitialisée", 2000)
    
    def show_status_message(self, message, duration=0):
        """Afficher un message dans la barre de statut"""
        self.status_label.setText(message)
        if duration > 0:
            self.status_timer.start(duration)
    
    def save_current_session(self):
        """Sauvegarder la session actuelle"""
        save_recent_files(
            self.settings,
            self.rh_paths,
            self.ext_path,
            self.template_path,
            self.certificateur
        )
        self.update_recent_menu()
    
    def load_recent_files_menu(self):
        """Charger le menu des fichiers récents"""
        self.update_recent_menu()
    
    def update_recent_menu(self):
        """Mettre à jour le menu des fichiers récents"""
        self.recent_menu.clear()
        
        recent_list = load_recent_files(self.settings)
        if not recent_list:
            action = QAction("(Aucun fichier récent)", self)
            action.setEnabled(False)
            self.recent_menu.addAction(action)
            return
        
        for i, recent in enumerate(recent_list):
            try:
                date = datetime.fromisoformat(recent["date"]).strftime("%d/%m/%Y %H:%M")
                text = f"{recent['certificateur']} - {date}"
                action = QAction(text, self)
                action.triggered.connect(lambda checked, r=recent: self.load_recent_session(r))
                self.recent_menu.addAction(action)
            except (KeyError, ValueError):
                continue
    
    def load_recent_session(self, recent):
        """Charger une session récente"""
        try:
            # Vérifier que les fichiers existent
            missing_files = []
            
            if not all(os.path.exists(f) for f in recent["rh_files"]):
                missing_files.append("fichiers RH")
            
            if not os.path.exists(recent["ext_file"]):
                missing_files.append("fichier d'extraction")
            
            if not os.path.exists(recent["template_file"]):
                missing_files.append("template")
            
            if missing_files:
                show_error_message(
                    self,
                    "Fichiers manquants",
                    f"Impossible de charger la session car ces fichiers sont manquants:\n\n{', '.join(missing_files)}"
                )
                return
            
            # Charger la session
            self.loading_page.cert_input.setText(recent["certificateur"])
            self.rh_paths = recent["rh_files"]
            self.ext_path = recent["ext_file"]
            self.template_path = recent["template_file"]
            
            # Mettre à jour l'affichage
            self.loading_page.update_rh_display()
            self.loading_page.ext_label.setText(f"📄 {os.path.basename(self.ext_path)}")
            self.loading_page.ext_valid_label.setText("✓")
            self.loading_page.ext_valid_label.setStyleSheet("color: #4caf50; font-weight: bold; font-size: 16px;")
            self.loading_page.template_label.setText(f"📋 {os.path.basename(self.template_path)}")
            self.loading_page.template_valid_label.setText("✓")
            self.loading_page.template_valid_label.setStyleSheet("color: #4caf50; font-weight: bold; font-size: 16px;")
            
            self.loading_page.check_can_process()
            self.show_status_message("Session récente chargée", 3000)
            
        except Exception as e:
            show_error_message(self, "Erreur", f"Impossible de charger la session:\n{str(e)}")

    def closeEvent(self, event):
        reply = show_question_message(
            self,
            "Confirmation",
            "Voulez-vous vraiment quitter ? Les modifications non sauvegardées seront perdues."
        )
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()