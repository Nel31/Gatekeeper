"""
Page de chargement des fichiers (Étape 1)
"""

import os
import pandas as pd
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QLineEdit, QFileDialog, QGroupBox, 
                            QListWidget, QProgressBar)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from ui.styles import WARNING_MESSAGE_STYLE, VALID_ICON_STYLE
from ui.utils import get_last_directory, save_last_directory, format_file_size


class LoadingPage(QWidget):
    """Page de chargement des fichiers"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setup_ui()
    
    def setup_ui(self):
        """Configurer l'interface de la page"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Titre avec sous-titre
        self.create_title_section(layout)
        
        # Conteneur pour les champs
        self.create_fields_section(layout)
        
        # Message d'aide contextuel
        self.create_help_message(layout)
        
        # Bouton de traitement
        self.create_process_button(layout)
        
        # Barre de progression
        self.create_progress_section(layout)
        
        layout.addStretch()
    
    def create_title_section(self, parent_layout):
        """Créer la section titre"""
        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        title_layout.setSpacing(5)
        
        title = QLabel("📁 Chargement des données")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_layout.addWidget(title)
        
        subtitle = QLabel("Veuillez renseigner toutes les informations nécessaires pour lancer la certification")
        subtitle.setStyleSheet("color: #666; font-size: 13px;")
        title_layout.addWidget(subtitle)
        
        parent_layout.addWidget(title_widget)
    
    def create_fields_section(self, parent_layout):
        """Créer la section des champs de saisie"""
        fields_widget = QWidget()
        fields_layout = QVBoxLayout(fields_widget)
        fields_layout.setSpacing(15)
        
        # Nom du certificateur
        self.create_certificateur_section(fields_layout)
        
        # Fichiers RH
        self.create_rh_files_section(fields_layout)
        
        # Fichier d'extraction
        self.create_extraction_section(fields_layout)
        
        # Template
        self.create_template_section(fields_layout)
        
        parent_layout.addWidget(fields_widget)
    
    def create_certificateur_section(self, parent_layout):
        """Créer la section certificateur"""
        cert_group = QGroupBox("Certificateur")
        cert_layout = QVBoxLayout()
        cert_layout.setSpacing(10)
        
        cert_input_layout = QHBoxLayout()
        self.cert_input = QLineEdit()
        self.cert_input.setPlaceholderText("Entrez votre nom complet...")
        self.cert_input.textChanged.connect(self.check_can_process)
        self.cert_input.setToolTip("Votre nom sera associé à toutes les validations de cette session")
        cert_input_layout.addWidget(self.cert_input)
        
        # Indicateur de validation
        self.cert_valid_label = QLabel()
        cert_input_layout.addWidget(self.cert_valid_label)
        
        cert_layout.addLayout(cert_input_layout)
        cert_group.setLayout(cert_layout)
        parent_layout.addWidget(cert_group)
    
    def create_rh_files_section(self, parent_layout):
        """Créer la section fichiers RH"""
        rh_group = QGroupBox("Fichiers RH")
        rh_layout = QVBoxLayout()
        
        rh_button_layout = QHBoxLayout()
        self.rh_button = QPushButton("📂 Sélectionner les fichiers RH")
        self.rh_button.clicked.connect(self.select_rh_files)
        self.rh_button.setToolTip("Sélectionnez un ou plusieurs fichiers Excel contenant les données RH de référence")
        rh_button_layout.addWidget(self.rh_button)
        
        self.rh_count_label = QLabel()
        rh_button_layout.addWidget(self.rh_count_label)
        rh_button_layout.addStretch()
        
        rh_layout.addLayout(rh_button_layout)
        
        # Liste des fichiers RH
        self.rh_list = QListWidget()
        self.rh_list.setMaximumHeight(80)
        self.rh_list.setVisible(False)
        rh_layout.addWidget(self.rh_list)
        
        # Mini résumé RH
        self.rh_summary = QLabel()
        self.rh_summary.setStyleSheet("color: #666; font-size: 12px; padding: 5px;")
        rh_layout.addWidget(self.rh_summary)
        
        rh_group.setLayout(rh_layout)
        parent_layout.addWidget(rh_group)
    
    def create_extraction_section(self, parent_layout):
        """Créer la section fichier d'extraction"""
        ext_group = QGroupBox("Fichier d'extraction")
        ext_layout = QVBoxLayout()
        
        ext_button_layout = QHBoxLayout()
        self.ext_button = QPushButton("📄 Sélectionner le fichier d'extraction")
        self.ext_button.clicked.connect(self.select_ext_file)
        self.ext_button.setToolTip("Fichier Excel exporté depuis l'application à auditer")
        ext_button_layout.addWidget(self.ext_button)
        
        self.ext_valid_label = QLabel()
        ext_button_layout.addWidget(self.ext_valid_label)
        ext_button_layout.addStretch()
        
        ext_layout.addLayout(ext_button_layout)
        
        self.ext_label = QLabel("Aucun fichier sélectionné")
        self.ext_label.setStyleSheet("color: #666; padding: 5px;")
        ext_layout.addWidget(self.ext_label)
        
        # Mini résumé extraction
        self.ext_summary = QLabel()
        self.ext_summary.setStyleSheet("color: #666; font-size: 12px; padding: 5px;")
        ext_layout.addWidget(self.ext_summary)
        
        ext_group.setLayout(ext_layout)
        parent_layout.addWidget(ext_group)
    
    def create_template_section(self, parent_layout):
        """Créer la section template"""
        template_group = QGroupBox("Template de rapport")
        template_layout = QVBoxLayout()
        
        template_button_layout = QHBoxLayout()
        self.template_button = QPushButton("📋 Sélectionner le template")
        self.template_button.clicked.connect(self.select_template_file)
        self.template_button.setToolTip("Template Excel qui sera utilisé pour générer le rapport final")
        template_button_layout.addWidget(self.template_button)
        
        self.template_valid_label = QLabel()
        template_button_layout.addWidget(self.template_valid_label)
        template_button_layout.addStretch()
        
        template_layout.addLayout(template_button_layout)
        
        self.template_label = QLabel("Aucun fichier sélectionné")
        self.template_label.setStyleSheet("color: #666; padding: 5px;")
        template_layout.addWidget(self.template_label)
        
        template_group.setLayout(template_layout)
        parent_layout.addWidget(template_group)
    
    def create_help_message(self, parent_layout):
        """Créer le message d'aide contextuel"""
        self.help_message = QLabel()
        self.help_message.setStyleSheet(WARNING_MESSAGE_STYLE)
        self.help_message.setWordWrap(True)
        self.help_message.setVisible(False)
        parent_layout.addWidget(self.help_message)
    
    def create_process_button(self, parent_layout):
        """Créer le bouton de traitement"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.process_button = QPushButton("🚀 Lancer le traitement")
        self.process_button.setObjectName("primaryButton")
        self.process_button.clicked.connect(self.parent_window.process_data)
        self.process_button.setEnabled(False)
        self.process_button.setMinimumWidth(200)
        button_layout.addWidget(self.process_button)
        
        button_layout.addStretch()
        parent_layout.addLayout(button_layout)
    
    def create_progress_section(self, parent_layout):
        """Créer la section de progression"""
        progress_widget = QWidget()
        progress_layout = QVBoxLayout(progress_widget)
        progress_layout.setSpacing(5)
        
        self.progress_label = QLabel()
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setVisible(False)
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        parent_layout.addWidget(progress_widget)
    
    def select_rh_files(self):
        """Sélectionner les fichiers RH"""
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            "Sélectionner les fichiers RH",
            get_last_directory(self.parent_window.settings),
            "Fichiers Excel (*.xlsx)"
        )
        if files:
            self.parent_window.rh_paths = files
            self.update_rh_display()
            save_last_directory(self.parent_window.settings, files[0])
            self.check_can_process()
            
            # Analyser rapidement le premier fichier
            self.analyze_rh_files(files)
    
    def analyze_rh_files(self, files):
        """Analyser rapidement les fichiers RH"""
        try:
            df = pd.read_excel(files[0], nrows=5)
            self.rh_summary.setText(f"📊 {len(df.columns)} colonnes détectées")
        except Exception:
            self.rh_summary.setText("⚠️ Erreur lors de l'analyse du fichier")
    
    def update_rh_display(self):
        """Mettre à jour l'affichage des fichiers RH"""
        if self.parent_window.rh_paths:
            self.rh_count_label.setText(f"✓ {len(self.parent_window.rh_paths)} fichier(s)")
            self.rh_count_label.setStyleSheet("color: #4caf50; font-weight: bold;")
            
            # Afficher la liste
            self.rh_list.clear()
            for path in self.parent_window.rh_paths:
                self.rh_list.addItem(os.path.basename(path))
            self.rh_list.setVisible(True)
        else:
            self.rh_count_label.setText("")
            self.rh_list.setVisible(False)
            self.rh_summary.setText("")
    
    def select_ext_file(self):
        """Sélectionner le fichier d'extraction"""
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner le fichier d'extraction",
            get_last_directory(self.parent_window.settings),
            "Fichiers Excel (*.xlsx)"
        )
        if file:
            self.parent_window.ext_path = file
            self.ext_label.setText(f"📄 {os.path.basename(file)}")
            self.ext_valid_label.setText("✓")
            self.ext_valid_label.setStyleSheet(VALID_ICON_STYLE)
            save_last_directory(self.parent_window.settings, file)
            self.check_can_process()
            
            # Analyser rapidement le fichier
            self.analyze_ext_file(file)
    
    def analyze_ext_file(self, file):
        """Analyser rapidement le fichier d'extraction"""
        try:
            df = pd.read_excel(file, nrows=5)
            size = os.path.getsize(file) / 1024 / 1024  # MB
            self.ext_summary.setText(f"📊 {len(df.columns)} colonnes, Taille: {format_file_size(os.path.getsize(file))}")
        except Exception:
            self.ext_summary.setText("⚠️ Erreur lors de l'analyse du fichier")
    
    def select_template_file(self):
        """Sélectionner le template"""
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner le template",
            get_last_directory(self.parent_window.settings),
            "Fichiers Excel (*.xlsx)"
        )
        if file:
            self.parent_window.template_path = file
            self.template_label.setText(f"📋 {os.path.basename(file)}")
            self.template_valid_label.setText("✓")
            self.template_valid_label.setStyleSheet(VALID_ICON_STYLE)
            save_last_directory(self.parent_window.settings, file)
            self.check_can_process()
    
    def check_can_process(self):
        """Vérifier si on peut lancer le traitement"""
        cert_ok = bool(self.cert_input.text().strip())
        rh_ok = bool(self.parent_window.rh_paths)
        ext_ok = bool(self.parent_window.ext_path)
        template_ok = bool(self.parent_window.template_path)
        
        # Feedback visuel pour le certificateur
        if cert_ok:
            self.cert_valid_label.setText("✓")
            self.cert_valid_label.setStyleSheet(VALID_ICON_STYLE)
        else:
            self.cert_valid_label.setText("")
        
        # Activer/désactiver le bouton
        can_process = cert_ok and rh_ok and ext_ok and template_ok
        self.process_button.setEnabled(can_process)
        
        # Message d'aide contextuel
        if not can_process:
            missing = []
            if not cert_ok:
                missing.append("nom du certificateur")
            if not rh_ok:
                missing.append("fichiers RH")
            if not ext_ok:
                missing.append("fichier d'extraction")
            if not template_ok:
                missing.append("template de rapport")
            
            self.help_message.setText(f"⚠️ Veuillez renseigner: {', '.join(missing)}")
            self.help_message.setVisible(True)
        else:
            self.help_message.setVisible(False)
    
    def get_certificateur(self):
        """Récupérer le nom du certificateur"""
        return self.cert_input.text().strip()
    
    def reset_form(self):
        """Réinitialiser le formulaire"""
        self.cert_input.clear()
        self.update_rh_display()
        self.ext_label.setText("Aucun fichier sélectionné")
        self.ext_valid_label.setText("")
        self.ext_summary.setText("")
        self.template_label.setText("Aucun fichier sélectionné")
        self.template_valid_label.setText("")
        self.process_button.setEnabled(False)
        self.help_message.setVisible(False)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)