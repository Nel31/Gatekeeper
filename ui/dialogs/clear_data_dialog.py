from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QCheckBox,
                            QPushButton, QLabel, QGroupBox)
from PyQt6.QtCore import Qt

class ClearDataDialog(QDialog):
    """Boîte de dialogue pour sélectionner les données à effacer"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Effacer les données mémorisées")
        self.setModal(True)
        self.setFixedSize(400, 300)
        self.setup_ui()
    
    def setup_ui(self):
        """Configurer l'interface"""
        layout = QVBoxLayout(self)
        
        # Message d'information
        info_label = QLabel("Sélectionnez les données à effacer :")
        info_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(info_label)
        
        # Groupe de cases à cocher
        group = QGroupBox("Données disponibles")
        group_layout = QVBoxLayout()
        
        # Cases à cocher
        self.check_recent = QCheckBox("Historique des fichiers récents")
        self.check_profiles = QCheckBox("Profils validés (whitelist)")
        self.check_directions = QCheckBox("Directions conservées")
        self.check_variations = QCheckBox("Variations d'écriture")
        
        group_layout.addWidget(self.check_recent)
        group_layout.addWidget(self.check_profiles)
        group_layout.addWidget(self.check_directions)
        group_layout.addWidget(self.check_variations)
        
        # Tout sélectionner
        self.check_all = QCheckBox("Tout sélectionner")
        self.check_all.toggled.connect(self.toggle_all)
        group_layout.addWidget(self.check_all)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        cancel_button = QPushButton("Annuler")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)
        
        clear_button = QPushButton("Effacer")
        clear_button.setObjectName("primaryButton")
        clear_button.clicked.connect(self.accept)
        buttons_layout.addWidget(clear_button)
        
        layout.addLayout(buttons_layout)
    
    def toggle_all(self, checked):
        """Sélectionner/désélectionner tout"""
        self.check_recent.setChecked(checked)
        self.check_profiles.setChecked(checked)
        self.check_directions.setChecked(checked)
        self.check_variations.setChecked(checked)
    
    def get_selected_items(self):
        """Récupérer les éléments sélectionnés"""
        items = []
        if self.check_recent.isChecked():
            items.append("Historique des fichiers récents")
        if self.check_profiles.isChecked():
            items.append("Profils validés (whitelist)")
        if self.check_directions.isChecked():
            items.append("Directions conservées")
        if self.check_variations.isChecked():
            items.append("Variations d'écriture")
        return items 