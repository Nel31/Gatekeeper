#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem,
    QGroupBox, QProgressBar, QTextEdit, QSplitter, QHeaderView,
    QMessageBox, QDialog, QDialogButtonBox, QRadioButton, QComboBox,
    QLineEdit, QTabWidget, QListWidget, QListWidgetItem, QCheckBox,
    QSpinBox, QFormLayout, QStyle, QStyledItemDelegate, QStyleOptionViewItem
)
from PySide6.QtCore import Qt, QThread, Signal, Slot, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QPalette, QColor, QIcon, QPixmap, QPainter, QBrush

# Import des modules métier existants
from rh_utils import charger_et_preparer_rh
from ext_utils import charger_et_preparer_ext
from match_utils import associer_rh_aux_utilisateurs
from anomalies import detecter_anomalies, extraire_cas_a_verifier
from profils_valides import ajouter_profil_valide
from directions_conservees import ajouter_direction_conservee
from report import inject_to_template


class WorkerThread(QThread):
    """Thread pour les opérations longues"""
    progress = Signal(int)
    status = Signal(str)
    finished = Signal(pd.DataFrame)
    error = Signal(str)
    
    def __init__(self, task_type, **kwargs):
        super().__init__()
        self.task_type = task_type
        self.kwargs = kwargs
        
    def run(self):
        try:
            if self.task_type == "load_files":
                self._load_files()
            elif self.task_type == "detect_anomalies":
                self._detect_anomalies()
            elif self.task_type == "generate_report":
                self._generate_report()
        except Exception as e:
            self.error.emit(str(e))
            
    def _load_files(self):
        self.status.emit("Chargement des fichiers RH...")
        self.progress.emit(10)
        
        rh_df = charger_et_preparer_rh(self.kwargs['rh_files'])
        self.progress.emit(30)
        
        self.status.emit("Chargement du fichier d'extraction...")
        ext_df = charger_et_preparer_ext(self.kwargs['ext_file'])
        self.progress.emit(50)
        
        self.status.emit("Association des données RH...")
        ext_df = associer_rh_aux_utilisateurs(ext_df, rh_df)
        self.progress.emit(70)
        
        self.status.emit("Détection des anomalies...")
        ext_df = detecter_anomalies(ext_df, self.kwargs['certificateur'])
        self.progress.emit(90)
        
        self.status.emit("Chargement terminé!")
        self.progress.emit(100)
        self.finished.emit(ext_df)
        
    def _generate_report(self):
        self.status.emit("Génération du rapport...")
        self.progress.emit(50)
        
        inject_to_template(
            self.kwargs['df'],
            self.kwargs['template_file'],
            self.kwargs['output_file'],
            self.kwargs['certificateur']
        )
        
        self.progress.emit(100)
        self.status.emit("Rapport généré avec succès!")


class DecisionDialog(QDialog):
    """Dialogue pour la prise de décision sur un cas"""
    
    def __init__(self, cas, parent=None):
        super().__init__(parent)
        self.cas = cas
        self.decision = None
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Décision sur le cas")
        self.setMinimumWidth(600)
        
        layout = QVBoxLayout(self)
        
        # Informations sur le cas
        info_group = QGroupBox("Informations utilisateur")
        info_layout = QFormLayout()
        
        fields = [
            ("Code utilisateur", self.cas.get('code_utilisateur', '')),
            ("Nom/Prénom", self.cas.get('nom_prenom', '')),
            ("Profil extraction", self.cas.get('profil', '')),
            ("Profil RH", self.cas.get('profil_rh', '')),
            ("Direction extraction", self.cas.get('direction', '')),
            ("Direction RH", self.cas.get('direction_rh', '')),
            ("Anomalie", self.cas.get('anomalie', ''))
        ]
        
        for label, value in fields:
            info_layout.addRow(QLabel(f"<b>{label}:</b>"), QLabel(str(value)))
            
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Options de décision
        decision_group = QGroupBox("Décision")
        decision_layout = QVBoxLayout()
        
        self.radio_buttons = {}
        anomalie = self.cas.get('anomalie', '')
        
        if "Changement de profil" in anomalie or "Changement de direction" in anomalie:
            options = [
                ("Modifier", "Mettre à jour selon le RH"),
                ("Conserver", "Tolérer l'écart et whitelister"),
                ("Désactiver", "Désactiver le compte")
            ]
        else:
            options = [
                ("Conserver", "Conserver le compte"),
                ("Désactiver", "Désactiver le compte")
            ]
            
        for value, description in options:
            radio = QRadioButton(f"{value} - {description}")
            self.radio_buttons[value] = radio
            decision_layout.addWidget(radio)
            
        decision_group.setLayout(decision_layout)
        layout.addWidget(decision_group)
        
        # Boutons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            parent=self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
    def accept(self):
        for value, radio in self.radio_buttons.items():
            if radio.isChecked():
                self.decision = value
                break
        super().accept()


class CertificateurMainWindow(QMainWindow):
    """Fenêtre principale de l'application"""
    
    def __init__(self):
        super().__init__()
        self.df = None
        self.certificateur = ""
        self.setup_ui()
        self.apply_dark_theme()
        
    def setup_ui(self):
        self.setWindowTitle("Certificateur de Comptes")
        self.setGeometry(100, 100, 1400, 900)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Onglets
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Onglet 1: Chargement et traitement
        self.setup_processing_tab()
        
        # Onglet 2: Configuration
        self.setup_config_tab()
        
        # Onglet 3: Historique
        self.setup_history_tab()
        
        # Barre de statut
        self.status_bar = self.statusBar()
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
    def setup_processing_tab(self):
        """Configuration de l'onglet principal"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Section 1: Informations certificateur
        cert_group = QGroupBox("Informations du certificateur")
        cert_layout = QHBoxLayout()
        cert_layout.addWidget(QLabel("Nom du certificateur:"))
        self.cert_input = QLineEdit()
        self.cert_input.setPlaceholderText("Entrez votre nom...")
        cert_layout.addWidget(self.cert_input)
        cert_group.setLayout(cert_layout)
        layout.addWidget(cert_group)
        
        # Section 2: Sélection des fichiers
        files_group = QGroupBox("Sélection des fichiers")
        files_layout = QVBoxLayout()
        
        # Fichiers RH
        rh_layout = QHBoxLayout()
        rh_layout.addWidget(QLabel("Fichiers RH:"))
        self.rh_list = QListWidget()
        self.rh_list.setMaximumHeight(80)
        rh_layout.addWidget(self.rh_list)
        
        rh_buttons = QVBoxLayout()
        self.btn_add_rh = QPushButton("Ajouter")
        self.btn_add_rh.clicked.connect(self.add_rh_files)
        self.btn_remove_rh = QPushButton("Retirer")
        self.btn_remove_rh.clicked.connect(self.remove_rh_file)
        rh_buttons.addWidget(self.btn_add_rh)
        rh_buttons.addWidget(self.btn_remove_rh)
        rh_layout.addLayout(rh_buttons)
        files_layout.addLayout(rh_layout)
        
        # Fichier extraction
        ext_layout = QHBoxLayout()
        ext_layout.addWidget(QLabel("Fichier extraction:"))
        self.ext_label = QLabel("Aucun fichier sélectionné")
        self.ext_label.setStyleSheet("QLabel { padding: 5px; }")
        ext_layout.addWidget(self.ext_label)
        self.btn_select_ext = QPushButton("Sélectionner")
        self.btn_select_ext.clicked.connect(self.select_ext_file)
        ext_layout.addWidget(self.btn_select_ext)
        files_layout.addLayout(ext_layout)
        
        # Template
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel("Template Excel:"))
        self.template_label = QLabel("Aucun fichier sélectionné")
        self.template_label.setStyleSheet("QLabel { padding: 5px; }")
        template_layout.addWidget(self.template_label)
        self.btn_select_template = QPushButton("Sélectionner")
        self.btn_select_template.clicked.connect(self.select_template_file)
        template_layout.addWidget(self.btn_select_template)
        files_layout.addLayout(template_layout)
        
        files_group.setLayout(files_layout)
        layout.addWidget(files_group)
        
        # Bouton de chargement
        self.btn_load = QPushButton("Charger et analyser les données")
        self.btn_load.clicked.connect(self.load_files)
        self.btn_load.setMinimumHeight(40)
        layout.addWidget(self.btn_load)
        
        # Section 3: Résultats
        results_splitter = QSplitter(Qt.Vertical)
        
        # Tableau des anomalies
        anomalies_group = QGroupBox("Anomalies détectées")
        anomalies_layout = QVBoxLayout()
        
        self.anomalies_table = QTableWidget()
        self.anomalies_table.setAlternatingRowColors(True)
        self.anomalies_table.setSelectionBehavior(QTableWidget.SelectRows)
        anomalies_layout.addWidget(self.anomalies_table)
        
        # Boutons d'action
        action_layout = QHBoxLayout()
        self.btn_review = QPushButton("Traiter les cas sélectionnés")
        self.btn_review.clicked.connect(self.review_selected_cases)
        self.btn_auto_decide = QPushButton("Décision automatique")
        self.btn_auto_decide.clicked.connect(self.auto_decide_cases)
        self.btn_generate_report = QPushButton("Générer le rapport")
        self.btn_generate_report.clicked.connect(self.generate_report)
        
        action_layout.addWidget(self.btn_review)
        action_layout.addWidget(self.btn_auto_decide)
        action_layout.addWidget(self.btn_generate_report)
        anomalies_layout.addLayout(action_layout)
        
        anomalies_group.setLayout(anomalies_layout)
        results_splitter.addWidget(anomalies_group)
        
        # Log des actions
        log_group = QGroupBox("Journal des actions")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        results_splitter.addWidget(log_group)
        
        layout.addWidget(results_splitter)
        
        # Désactiver les boutons au démarrage
        self.btn_review.setEnabled(False)
        self.btn_auto_decide.setEnabled(False)
        self.btn_generate_report.setEnabled(False)
        
        self.tabs.addTab(tab, "Traitement")
        
    def setup_config_tab(self):
        """Configuration de l'onglet de configuration"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Seuils
        thresholds_group = QGroupBox("Seuils de détection")
        thresholds_layout = QFormLayout()
        
        self.similarity_threshold = QSpinBox()
        self.similarity_threshold.setRange(0, 100)
        self.similarity_threshold.setValue(85)
        self.similarity_threshold.setSuffix("%")
        thresholds_layout.addRow("Seuil de similarité:", self.similarity_threshold)
        
        self.inactivity_threshold = QSpinBox()
        self.inactivity_threshold.setRange(1, 365)
        self.inactivity_threshold.setValue(120)
        self.inactivity_threshold.setSuffix(" jours")
        thresholds_layout.addRow("Seuil d'inactivité:", self.inactivity_threshold)
        
        thresholds_group.setLayout(thresholds_layout)
        layout.addWidget(thresholds_group)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()
        
        self.auto_whitelist = QCheckBox("Whitelister automatiquement les cas validés")
        self.auto_whitelist.setChecked(True)
        options_layout.addWidget(self.auto_whitelist)
        
        self.skip_reviewed = QCheckBox("Ignorer les cas déjà traités")
        self.skip_reviewed.setChecked(True)
        options_layout.addWidget(self.skip_reviewed)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        layout.addStretch()
        
        self.tabs.addTab(tab, "Configuration")
        
    def setup_history_tab(self):
        """Configuration de l'onglet historique"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Liste des profils whitelistés
        profiles_group = QGroupBox("Profils validés")
        profiles_layout = QVBoxLayout()
        self.profiles_table = QTableWidget()
        self.profiles_table.setColumnCount(4)
        self.profiles_table.setHorizontalHeaderLabels([
            "Profil extraction", "Profil RH", "Date validation", "Certificateur"
        ])
        profiles_layout.addWidget(self.profiles_table)
        profiles_group.setLayout(profiles_layout)
        layout.addWidget(profiles_group)
        
        # Liste des directions whitelistées
        directions_group = QGroupBox("Directions validées")
        directions_layout = QVBoxLayout()
        self.directions_table = QTableWidget()
        self.directions_table.setColumnCount(4)
        self.directions_table.setHorizontalHeaderLabels([
            "Direction extraction", "Direction RH", "Date validation", "Certificateur"
        ])
        directions_layout.addWidget(self.directions_table)
        directions_group.setLayout(directions_layout)
        layout.addWidget(directions_group)
        
        # Bouton de rafraîchissement
        self.btn_refresh_history = QPushButton("Rafraîchir l'historique")
        self.btn_refresh_history.clicked.connect(self.refresh_history)
        layout.addWidget(self.btn_refresh_history)
        
        self.tabs.addTab(tab, "Historique")
        
    def apply_dark_theme(self):
        """Applique un thème sombre moderne"""
        dark_stylesheet = """
        QMainWindow {
            background-color: #1e1e1e;
        }
        
        QWidget {
            background-color: #2d2d2d;
            color: #ffffff;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 10pt;
        }
        
        QGroupBox {
            background-color: #363636;
            border: 1px solid #4a4a4a;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        
        QPushButton {
            background-color: #0d7377;
            color: white;
            border: none;
            padding: 8px;
            border-radius: 4px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #14a085;
        }
        
        QPushButton:pressed {
            background-color: #0a5d61;
        }
        
        QPushButton:disabled {
            background-color: #4a4a4a;
            color: #888888;
        }
        
        QLineEdit, QTextEdit, QListWidget {
            background-color: #404040;
            border: 1px solid #555555;
            border-radius: 3px;
            padding: 5px;
            selection-background-color: #0d7377;
        }
        
        QTableWidget {
            background-color: #404040;
            gridline-color: #555555;
            border: 1px solid #555555;
        }
        
        QTableWidget::item {
            padding: 5px;
        }
        
        QTableWidget::item:selected {
            background-color: #0d7377;
        }
        
        QHeaderView::section {
            background-color: #2d2d2d;
            padding: 5px;
            border: 1px solid #555555;
            font-weight: bold;
        }
        
        QTabWidget::pane {
            border: 1px solid #555555;
            background-color: #2d2d2d;
        }
        
        QTabBar::tab {
            background-color: #363636;
            padding: 8px 15px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: #0d7377;
        }
        
        QProgressBar {
            border: 1px solid #555555;
            border-radius: 3px;
            text-align: center;
        }
        
        QProgressBar::chunk {
            background-color: #0d7377;
            border-radius: 3px;
        }
        
        QCheckBox::indicator {
            width: 15px;
            height: 15px;
        }
        
        QCheckBox::indicator:unchecked {
            background-color: #404040;
            border: 1px solid #555555;
            border-radius: 3px;
        }
        
        QCheckBox::indicator:checked {
            background-color: #0d7377;
            border: 1px solid #0d7377;
            border-radius: 3px;
        }
        """
        
        self.setStyleSheet(dark_stylesheet)
        
    def add_rh_files(self):
        """Ajouter des fichiers RH"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Sélectionner les fichiers RH",
            "",
            "Fichiers Excel (*.xlsx *.xls)"
        )
        
        for file in files:
            self.rh_list.addItem(os.path.basename(file))
            self.rh_list.item(self.rh_list.count() - 1).setData(Qt.UserRole, file)
            
    def remove_rh_file(self):
        """Retirer un fichier RH de la liste"""
        current = self.rh_list.currentRow()
        if current >= 0:
            self.rh_list.takeItem(current)
            
    def select_ext_file(self):
        """Sélectionner le fichier d'extraction"""
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner le fichier d'extraction",
            "",
            "Fichiers Excel (*.xlsx *.xls)"
        )
        
        if file:
            self.ext_file = file
            self.ext_label.setText(os.path.basename(file))
            
    def select_template_file(self):
        """Sélectionner le template Excel"""
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner le template Excel",
            "",
            "Fichiers Excel (*.xlsx *.xls)"
        )
        
        if file:
            self.template_file = file
            self.template_label.setText(os.path.basename(file))
            
    def load_files(self):
        """Charger et analyser les fichiers"""
        # Validation
        if not self.cert_input.text():
            QMessageBox.warning(self, "Attention", "Veuillez entrer le nom du certificateur")
            return
            
        if self.rh_list.count() == 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner au moins un fichier RH")
            return
            
        if not hasattr(self, 'ext_file'):
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner le fichier d'extraction")
            return
            
        self.certificateur = self.cert_input.text()
        
        # Récupérer les chemins des fichiers RH
        rh_files = []
        for i in range(self.rh_list.count()):
            item = self.rh_list.item(i)
            rh_files.append(item.data(Qt.UserRole))
            
        # Lancer le traitement dans un thread
        self.worker = WorkerThread(
            "load_files",
            rh_files=rh_files,
            ext_file=self.ext_file,
            certificateur=self.certificateur
        )
        
        self.worker.progress.connect(self.update_progress)
        self.worker.status.connect(self.update_status)
        self.worker.finished.connect(self.on_files_loaded)
        self.worker.error.connect(self.on_error)
        
        self.btn_load.setEnabled(False)
        self.worker.start()
        
    def update_progress(self, value):
        """Mettre à jour la barre de progression"""
        self.progress_bar.setValue(value)
        
    def update_status(self, message):
        """Mettre à jour le statut"""
        self.status_bar.showMessage(message)
        self.log(message)
        
    def log(self, message):
        """Ajouter un message au journal"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
    def on_files_loaded(self, df):
        """Callback après le chargement des fichiers"""
        self.df = df
        self.btn_load.setEnabled(True)
        self.display_anomalies()
        
        # Activer les boutons
        self.btn_review.setEnabled(True)
        self.btn_auto_decide.setEnabled(True)
        self.btn_generate_report.setEnabled(True)
        
        # Statistiques
        total = len(df)
        anomalies = len(df[df['anomalie'].str.len() > 0])
        self.log(f"Chargement terminé: {total} comptes analysés, {anomalies} anomalies détectées")
        
    def on_error(self, error_message):
        """Gestion des erreurs"""
        QMessageBox.critical(self, "Erreur", f"Une erreur est survenue:\n{error_message}")
        self.btn_load.setEnabled(True)
        self.progress_bar.setValue(0)
        
    def display_anomalies(self):
        """Afficher les anomalies dans le tableau"""
        if self.df is None:
            return
            
        # Filtrer les anomalies
        anomalies_df = self.df[self.df['anomalie'].str.len() > 0].copy()
        
        # Configurer le tableau
        self.anomalies_table.setRowCount(len(anomalies_df))
        self.anomalies_table.setColumnCount(8)
        self.anomalies_table.setHorizontalHeaderLabels([
            "Code", "Nom/Prénom", "Profil", "Profil RH", 
            "Direction", "Direction RH", "Anomalie", "Décision"
        ])
        
        # Remplir le tableau
        for i, (_, row) in enumerate(anomalies_df.iterrows()):
            items = [
                row.get('code_utilisateur', ''),
                row.get('nom_prenom', ''),
                row.get('profil', ''),
                row.get('profil_rh', ''),
                row.get('direction', ''),
                row.get('direction_rh', ''),
                row.get('anomalie', ''),
                row.get('decision_manuelle', '')
            ]
            
            for j, value in enumerate(items):
                item = QTableWidgetItem(str(value))
                if j == 7 and value:  # Colonne décision
                    if value == "Désactiver":
                        item.setBackground(QColor(255, 100, 100))
                    elif value == "Modifier":
                        item.setBackground(QColor(255, 200, 100))
                    elif value == "Conserver":
                        item.setBackground(QColor(100, 255, 100))
                self.anomalies_table.setItem(i, j, item)
                
        # Ajuster les colonnes
        self.anomalies_table.resizeColumnsToContents()
        
    def review_selected_cases(self):
        """Traiter les cas sélectionnés"""
        selected_rows = set()
        for item in self.anomalies_table.selectedItems():
            selected_rows.add(item.row())
            
        if not selected_rows:
            QMessageBox.information(self, "Information", "Veuillez sélectionner des cas à traiter")
            return
            
        for row in selected_rows:
            # Récupérer les données du cas
            code = self.anomalies_table.item(row, 0).text()
            cas = self.df[self.df['code_utilisateur'] == code].iloc[0]
            
            # Ouvrir le dialogue de décision
            dialog = DecisionDialog(cas, self)
            if dialog.exec() == QDialog.Accepted and dialog.decision:
                # Mettre à jour la décision
                self.df.loc[self.df['code_utilisateur'] == code, 'decision_manuelle'] = dialog.decision
                
                # Mettre à jour l'affichage
                self.anomalies_table.item(row, 7).setText(dialog.decision)
                
                # Gérer les whitelists si nécessaire
                if self.auto_whitelist.isChecked():
                    if dialog.decision in ["Modifier", "Conserver"]:
                        if "Changement de profil" in cas.get('anomalie', ''):
                            ajouter_profil_valide(cas, self.certificateur)
                        if "Changement de direction" in cas.get('anomalie', ''):
                            ajouter_direction_conservee(cas, self.certificateur)
                            
                self.log(f"Décision '{dialog.decision}' prise pour {code}")
                
    def auto_decide_cases(self):
        """Décision automatique pour les cas simples"""
        if self.df is None:
            return
            
        # Compter les cas traités
        count = 0
        
        # Traiter automatiquement les comptes inactifs
        mask = (self.df['anomalie'].str.contains('inactif', case=False)) & (self.df['decision_manuelle'] == '')
        self.df.loc[mask, 'decision_manuelle'] = 'Désactiver'
        count += mask.sum()
        
        self.log(f"Décision automatique appliquée à {count} cas")
        self.display_anomalies()
        
        if count > 0:
            QMessageBox.information(
                self, 
                "Décisions automatiques", 
                f"{count} comptes inactifs ont été marqués pour désactivation"
            )
            
    def generate_report(self):
        """Générer le rapport Excel"""
        if self.df is None:
            QMessageBox.warning(self, "Attention", "Aucune donnée à exporter")
            return
            
        if not hasattr(self, 'template_file'):
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un template Excel")
            return
            
        # Demander où sauvegarder
        output_file, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer le rapport",
            f"rapport_certification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "Fichiers Excel (*.xlsx)"
        )
        
        if not output_file:
            return
            
        # Préparer les données pour le rapport
        self.df['certificateur'] = self.certificateur
        self.df['recommendation'] = 'A certifier'
        
        # Mapper les décisions
        decision_map = {
            "Conserver": ("A conserver", "Conservé"),
            "Désactiver": ("A desactiver", "Désactivé"),
            "Modifier": ("A Modifier", "Modifié"),
        }
        
        self.df['decision'] = self.df['decision_manuelle'].map(
            lambda x: decision_map.get(x, ("", ""))[0]
        )
        self.df['execution_reco_decision'] = self.df['decision_manuelle'].map(
            lambda x: decision_map.get(x, ("", ""))[1]
        )
        
        # Lancer la génération dans un thread
        self.worker = WorkerThread(
            "generate_report",
            df=self.df,
            template_file=self.template_file,
            output_file=output_file,
            certificateur=self.certificateur
        )
        
        self.worker.progress.connect(self.update_progress)
        self.worker.status.connect(self.update_status)
        self.worker.finished.connect(lambda _: self.on_report_generated(output_file))
        self.worker.error.connect(self.on_error)
        
        self.worker.start()
        
    def on_report_generated(self, output_file):
        """Callback après génération du rapport"""
        QMessageBox.information(
            self,
            "Rapport généré",
            f"Le rapport a été généré avec succès:\n{output_file}"
        )
        
        # Proposer d'ouvrir le fichier
        reply = QMessageBox.question(
            self,
            "Ouvrir le rapport",
            "Voulez-vous ouvrir le rapport maintenant?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            os.startfile(output_file)
            
    def refresh_history(self):
        """Rafraîchir l'historique des validations"""
        try:
            # Charger les profils validés
            if os.path.exists("profils_valides.csv"):
                profils_df = pd.read_csv("profils_valides.csv")
                self.profiles_table.setRowCount(len(profils_df))
                
                for i, row in profils_df.iterrows():
                    for j, value in enumerate(row):
                        item = QTableWidgetItem(str(value))
                        self.profiles_table.setItem(i, j, item)
                        
            # Charger les directions validées
            if os.path.exists("directions_conservees.csv"):
                directions_df = pd.read_csv("directions_conservees.csv")
                self.directions_table.setRowCount(len(directions_df))
                
                for i, row in directions_df.iterrows():
                    for j, value in enumerate(row):
                        item = QTableWidgetItem(str(value))
                        self.directions_table.setItem(i, j, item)
                        
            self.log("Historique rafraîchi")
            
        except Exception as e:
            self.log(f"Erreur lors du rafraîchissement: {str(e)}")


class SplashScreen(QWidget):
    """Écran de démarrage animé"""
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(600, 400)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Conteneur avec fond
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-radius: 20px;
            }
        """)
        container_layout = QVBoxLayout(container)
        
        # Logo/Titre
        title = QLabel("Certificateur de Comptes")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 28px;
                font-weight: bold;
                padding: 20px;
            }
        """)
        container_layout.addWidget(title)
        
        # Version
        version = QLabel("Version 2.0")
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 14px;
            }
        """)
        container_layout.addWidget(version)
        
        # Animation de chargement
        self.loading_label = QLabel("Chargement...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("""
            QLabel {
                color: #0d7377;
                font-size: 16px;
                padding: 20px;
            }
        """)
        container_layout.addWidget(self.loading_label)
        
        # Barre de progression
        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #555555;
                border-radius: 5px;
                text-align: center;
                background-color: #2d2d2d;
                color: white;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #0d7377;
                border-radius: 3px;
            }
        """)
        container_layout.addWidget(self.progress)
        
        # Copyright
        copyright_label = QLabel("© 2024 - Développé avec ❤️")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 12px;
                padding: 10px;
            }
        """)
        container_layout.addWidget(copyright_label)
        
        layout.addWidget(container)
        
        # Timer pour la simulation de chargement
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.current_progress = 0
        
    def start_loading(self):
        """Démarrer l'animation de chargement"""
        self.timer.start(30)
        
    def update_progress(self):
        """Mettre à jour la progression"""
        self.current_progress += 2
        self.progress.setValue(self.current_progress)
        
        if self.current_progress >= 100:
            self.timer.stop()
            self.close()


def main():
    """Point d'entrée principal"""
    app = QApplication(sys.argv)
    app.setApplicationName("Certificateur de Comptes")
    app.setOrganizationName("VotreOrganisation")
    
    # Afficher l'écran de démarrage
    splash = SplashScreen()
    splash.show()
    splash.start_loading()
    
    # Créer la fenêtre principale
    window = CertificateurMainWindow()
    
    # Afficher la fenêtre principale après le splash
    QTimer.singleShot(3000, lambda: (window.show(), splash.close()))
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()