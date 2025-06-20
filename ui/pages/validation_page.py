"""
Page de validation manuelle (Étape 3) - Version refactorisée avec UX améliorée
"""

import pandas as pd
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QGroupBox, QRadioButton, QTextEdit, 
                            QProgressBar, QFrame, QSizePolicy, QButtonGroup,
                            QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                            QComboBox, QLineEdit, QFileDialog)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, pyqtSignal

from core.anomalies import extraire_cas_a_verifier
from mapping.profils_valides import (
    ajouter_profil_valide, ajouter_variation_profil, ajouter_changement_profil
)
from mapping.directions_conservees import (
    ajouter_direction_valide, ajouter_variation_direction, ajouter_changement_direction
)
from core.report import generer_rapport


class ValidationPage(QWidget):
    """Page de validation manuelle avec UX moderne"""
    
    back_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.current_cas_index = 0
        self.df = None
        self.certificateur = None
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setup_ui()
    
    def resizeEvent(self, event):
        """Gérer la responsivité lors du redimensionnement"""
        super().resizeEvent(event)
        self.adjust_layout_for_size()
    
    def adjust_layout_for_size(self):
        """Ajuster le layout selon la taille de la fenêtre"""
        if hasattr(self, 'main_container'):
            width = self.width()
            
            # Ajustements selon la largeur de la fenêtre
            if width < 1000:
                # Écrans très petits - priorité à la comparaison
                layout = self.main_container.layout()
                if layout and layout.count() >= 3:
                    layout.setStretchFactor(layout.itemAt(0).widget(), 20)  # Info: 20%
                    layout.setStretchFactor(layout.itemAt(1).widget(), 55)  # Comparaison: 55%
                    layout.setStretchFactor(layout.itemAt(2).widget(), 25)  # Actions: 25%
            elif width < 1200:
                # Écrans moyens
                layout = self.main_container.layout()
                if layout and layout.count() >= 3:
                    layout.setStretchFactor(layout.itemAt(0).widget(), 25)  # Info: 25%
                    layout.setStretchFactor(layout.itemAt(1).widget(), 50)  # Comparaison: 50%
                    layout.setStretchFactor(layout.itemAt(2).widget(), 25)  # Actions: 25%
            else:
                # Grandes résolutions - proportions optimales
                layout = self.main_container.layout()
                if layout and layout.count() >= 3:
                    layout.setStretchFactor(layout.itemAt(0).widget(), 30)  # Info: 30%
                    layout.setStretchFactor(layout.itemAt(1).widget(), 45)  # Comparaison: 45%
                    layout.setStretchFactor(layout.itemAt(2).widget(), 25)  # Actions: 25%
    
    def setup_ui(self):
        """Configurer l'interface moderne et responsive"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)  # Marges optimisées
        layout.setSpacing(12)  # Espacement réduit pour plus d'espace
        
        # Header compact avec progression
        self.create_compact_header(layout)
        
        # Layout principal responsive
        self.create_main_content(layout)
        
        # Navigation en bas
        self.create_navigation_section(layout)
    
    def create_compact_header(self, parent_layout):
        """Header ultra-compact avec titre et progression"""
        header_container = QWidget()
        header_container.setFixedHeight(60)  # Hauteur réduite
        header_container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #001122, stop:1 #000000);
                border-radius: 8px;
            }
        """)
        
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(15, 8, 15, 8)  # Marges réduites
        header_layout.setSpacing(6)  # Espacement réduit
        
        # Titre et compteur
        title_row = QHBoxLayout()
        title = QLabel("✅ Validation Manuelle")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))  # Taille réduite
        title.setStyleSheet("color: #ffffff; background: transparent;")
        title_row.addWidget(title)
        
        title_row.addStretch()
        
        self.validation_counter = QLabel("Cas 1 sur 6")
        self.validation_counter.setStyleSheet("""
            color: #0099ff; font-weight: bold; font-size: 13px; 
            background: transparent; padding: 3px 10px;
            border: 1px solid #0099ff; border-radius: 12px;
        """)
        title_row.addWidget(self.validation_counter)
        
        header_layout.addLayout(title_row)
        
        # Barre de progression moderne
        self.validation_progress = QProgressBar()
        self.validation_progress.setFixedHeight(4)  # Plus fine
        self.validation_progress.setTextVisible(False)
        self.validation_progress.setStyleSheet("""
            QProgressBar {
                background-color: #1a1a1a;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0066cc, stop:1 #0099ff);
                border-radius: 2px;
            }
        """)
        header_layout.addWidget(self.validation_progress)
        
        parent_layout.addWidget(header_container)
    
    def create_main_content(self, parent_layout):
        """Contenu principal responsive en 3 colonnes"""
        self.main_container = QWidget()  # Stocker comme attribut pour la responsivité
        main_layout = QHBoxLayout(self.main_container)
        main_layout.setSpacing(15)  # Espacement réduit pour plus d'espace
        
        # Colonne 1: Informations utilisateur + Anomalie
        self.create_user_info_column(main_layout)
        
        # Colonne 2: Comparaison visuelle (plus d'espace)
        self.create_comparison_column(main_layout)
        
        # Colonne 3: Actions et décisions
        self.create_actions_column(main_layout)
        
        parent_layout.addWidget(self.main_container)
    
    def create_user_info_column(self, parent_layout):
        """Colonne des informations utilisateur avec card moderne"""
        left_column = QWidget()
        left_column.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        left_layout = QVBoxLayout(left_column)
        left_layout.setSpacing(15)
        
        # Card utilisateur
        user_card = self.create_modern_card("👤 Informations Utilisateur")
        user_layout = QVBoxLayout()
        
        self.user_info_label = QLabel()
        self.user_info_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                line-height: 1.6;
                background: transparent;
                padding: 10px;
            }
        """)
        self.user_info_label.setWordWrap(True)
        user_layout.addWidget(self.user_info_label)
        
        user_card.setLayout(user_layout)
        left_layout.addWidget(user_card)
        
        # Card anomalie avec badge proéminent (stockée pour masquage)
        self.anomaly_card = self.create_modern_card("⚠️ Anomalie Détectée")
        anomaly_layout = QVBoxLayout()
        
        # Badge d'anomalie coloré
        self.anomaly_badge = QLabel()
        self.anomaly_badge.setStyleSheet("""
            QLabel {
                background-color: #ff9800;
                color: #000000;
                font-weight: bold;
                font-size: 13px;
                padding: 12px 16px;
                border-radius: 8px;
                border-left: 4px solid #ff6f00;
            }
        """)
        self.anomaly_badge.setWordWrap(True)
        anomaly_layout.addWidget(self.anomaly_badge)
        
        self.anomaly_card.setLayout(anomaly_layout)
        left_layout.addWidget(self.anomaly_card)
        
        left_layout.addStretch()
        parent_layout.addWidget(left_column, 30)  # 30% de l'espace
    
    def create_comparison_column(self, parent_layout):
        """Colonne de comparaison visuelle améliorée"""
        center_column = QWidget()
        center_column.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        center_layout = QVBoxLayout(center_column)
        center_layout.setSpacing(15)
        
        # Card de comparaison avec design moderne
        comparison_card = self.create_modern_card("🔍 Comparaison Extraction vs RH")
        comparison_layout = QVBoxLayout()
        
        # Container pour la comparaison côte-à-côte
        self.comparison_container = QWidget()
        self.comparison_container.setStyleSheet("""
            QWidget {
                background-color: #0a0a0a;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        self.comparison_layout = QVBoxLayout(self.comparison_container)
        self.comparison_layout.setSpacing(12)
        
        comparison_layout.addWidget(self.comparison_container)
        comparison_card.setLayout(comparison_layout)
        center_layout.addWidget(comparison_card)
        
        parent_layout.addWidget(center_column, 45)  # 45% de l'espace pour plus de place
    
    def create_actions_column(self, parent_layout):
        """Colonne des actions avec design moderne et responsive"""
        right_column = QWidget()
        right_column.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        right_column.setMinimumWidth(250)  # Largeur minimum pour éviter le tassement
        right_column.setMaximumWidth(320)  # Largeur maximum pour responsivité
        right_layout = QVBoxLayout(right_column)
        right_layout.setSpacing(12)
        right_layout.setContentsMargins(5, 0, 5, 0)  # Marges réduites
        
        # Card des actions (stockée pour masquage)
        self.actions_card = self.create_modern_card("🎯 Actions Possibles")
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(8)  # Espacement réduit entre radio buttons
        
        # Radio buttons modernes
        self.create_modern_radio_buttons(actions_layout)
        
        # Zone de commentaire
        comment_label = QLabel("💬 Commentaire (optionnel):")
        comment_label.setStyleSheet("""
            color: #ffffff; font-weight: bold; font-size: 12px;
            background: transparent; margin-top: 10px;
        """)
        actions_layout.addWidget(comment_label)
        
        self.comment_edit = QTextEdit()
        self.comment_edit.setPlaceholderText("Justifiez votre décision...")
        self.comment_edit.setMaximumHeight(80)  # Hauteur réduite
        self.comment_edit.setStyleSheet("""
            QTextEdit {
                background-color: #0d0d0d;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 8px;
                color: #fff;
                font-size: 11px;
            }
            QTextEdit:focus {
                border: 2px solid #0066cc;
            }
        """)
        actions_layout.addWidget(self.comment_edit)
        
        # Boutons d'action améliorés
        self.create_action_buttons(actions_layout)
        
        self.actions_card.setLayout(actions_layout)
        right_layout.addWidget(self.actions_card)
        
        right_layout.addStretch()
        parent_layout.addWidget(right_column, 25)  # 25% de l'espace
    
    def create_modern_card(self, title):
        """Créer une card moderne avec titre"""
        card = QGroupBox(title)
        card.setStyleSheet("""
            QGroupBox {
                background-color: #0d0d0d;
                border: 1px solid #1a1a1a;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 15px;
                font-weight: bold;
                font-size: 14px;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 6px 12px;
                background-color: #0066cc;
                border-radius: 6px;
                color: #ffffff;
                font-weight: bold;
            }
        """)
        return card
    
    def create_modern_radio_buttons(self, parent_layout):
        """Créer des radio buttons modernes avec groupement exclusif"""
        # Créer le groupe pour sélection exclusive
        self.radio_group = QButtonGroup(self)
        
        modifier_container = self.create_styled_radio(
            "✏️ Modifier", "Mettre à jour selon le RH", "#2196F3"
        )
        conserver_container = self.create_styled_radio(
            "✓ Conserver", "Tolérer l'écart détecté", "#4CAF50"
        )
        desactiver_container = self.create_styled_radio(
            "❌ Désactiver", "Supprimer le compte", "#F44336"
        )
        
        # Ajouter les radio buttons au groupe
        self.radio_group.addButton(self.radio_modifier)
        self.radio_group.addButton(self.radio_conserver)
        self.radio_group.addButton(self.radio_desactiver)
        
        parent_layout.addWidget(modifier_container)
        parent_layout.addWidget(conserver_container)
        parent_layout.addWidget(desactiver_container)
    
    def create_styled_radio(self, title, description, color):
        """Créer un radio button stylé avec description responsive"""
        container = QWidget()
        container.setStyleSheet(f"""
            QWidget {{
                background-color: #0a0a0a;
                border: 1px solid {color}40;
                border-radius: 6px;
                padding: 8px;
            }}
            QWidget:hover {{
                background-color: #111111;
                border: 1px solid {color}80;
            }}
        """)
        
        layout = QVBoxLayout(container)
        layout.setSpacing(2)  # Espacement ultra-réduit
        layout.setContentsMargins(6, 6, 6, 6)  # Marges réduites
        
        # Radio button avec titre
        radio = QRadioButton(title)
        radio.setStyleSheet(f"""
            QRadioButton {{
                color: {color};
                font-weight: bold;
                font-size: 12px;
                spacing: 6px;
                background: transparent;
            }}
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 8px;
            }}
            QRadioButton::indicator:unchecked {{
                border: 2px solid {color};
                background-color: transparent;
            }}
            QRadioButton::indicator:checked {{
                border: 2px solid {color};
                background-color: {color};
            }}
        """)
        # Ajout du tooltip sur le radio button
        radio.setToolTip(description)
        layout.addWidget(radio)
        
        # Stocker les références (radio button ET conteneur)
        if "Modifier" in title:
            self.radio_modifier = radio
            self.modifier_container = container
        elif "Conserver" in title:
            self.radio_conserver = radio
            self.conserver_container = container
        elif "Désactiver" in title:
            self.radio_desactiver = radio
            self.desactiver_container = container
        
        return container
    
    def create_action_buttons(self, parent_layout):
        """Créer les boutons d'action améliorés et responsives"""
        buttons_layout = QVBoxLayout()  # Layout vertical pour économiser l'espace
        buttons_layout.setSpacing(8)  # Espacement réduit
        
        # Bouton "Passer ce cas" amélioré avec texte explicite
        self.skip_button = QPushButton("⏭️ Passer ce cas")
        self.skip_button.setFixedHeight(35)  # Hauteur réduite
        self.skip_button.setToolTip("Passer au cas suivant sans prendre de décision")
        self.skip_button.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                border: none;
                border-radius: 5px;
                color: #000;
                font-weight: bold;
                font-size: 11px;
                padding: 6px 10px;
            }
            QPushButton:hover { 
                background-color: #ffb84d;
                color: #000;
            }
        """)
        self.skip_button.clicked.connect(self.skip_case)
        buttons_layout.addWidget(self.skip_button)
        
        # Bouton "Valider" principal
        self.validate_button = QPushButton("✅ Valider la décision")
        self.validate_button.setFixedHeight(40)  # Hauteur réduite
        self.validate_button.setStyleSheet("""
            QPushButton {
                background-color: #00cc44;
                border: none;
                border-radius: 5px;
                padding: 8px 12px;
                color: #000;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover { 
                background-color: #00ff55;
                color: #000;
            }
        """)
        self.validate_button.clicked.connect(self.validate_decision)
        buttons_layout.addWidget(self.validate_button)
        
        parent_layout.addLayout(buttons_layout)
    
    def create_navigation_section(self, parent_layout):
        """Créer la section de navigation compacte"""
        nav_container = QWidget()
        nav_container.setFixedHeight(50)
        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 10, 0, 10)
        
        self.back_to_table_button = QPushButton("← Retour au tableau")
        self.back_to_table_button.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 10px 20px;
                color: #ccc;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #333; color: #fff; }
        """)
        self.back_to_table_button.clicked.connect(lambda: self.parent_window.go_to_step(1))
        nav_layout.addWidget(self.back_to_table_button)
        
        nav_layout.addStretch()
        
        self.finish_validation_button = QPushButton("Terminer la validation →")
        self.finish_validation_button.setStyleSheet("""
            QPushButton {
                background-color: #0066cc;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                color: white;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #0080ff; }
        """)
        self.finish_validation_button.clicked.connect(lambda: self.parent_window.go_to_step(3))
        self.finish_validation_button.setVisible(False)
        nav_layout.addWidget(self.finish_validation_button)
        
        parent_layout.addWidget(nav_container)
    
    def display_case_info(self, cas):
        """Afficher les informations du cas avec mise en forme moderne"""
        try:
            jours = cas.get('days_inactive', '')
            if isinstance(jours, (int, float)) and not pd.isna(jours):
                jours_affiche = f"{jours:.0f} jours"
                inactivity_color = "#ff5555" if jours > 120 else "#00ff55"
            else:
                jours_affiche = "Non renseigné"
                inactivity_color = "#999999"
        except:
            jours_affiche = "Non renseigné"
            inactivity_color = "#999999"
        
        info_html = f"""
        <div style="line-height: 1.8;">
            <p><b style="color: #0099ff;">Code utilisateur:</b><br>
               <span style="font-size: 16px; color: #ffffff;">{cas.get('code_utilisateur', 'N/A')}</span></p>
            
            <p><b style="color: #0099ff;">Nom/Prénom:</b><br>
               <span style="font-size: 16px; color: #ffffff;">{cas.get('nom_prenom', 'N/A')}</span></p>
            
            <p><b style="color: #0099ff;">Inactivité:</b><br>
               <span style="font-size: 14px; color: {inactivity_color};">{jours_affiche}</span></p>
        </div>
        """
        
        self.user_info_label.setText(info_html)
        
        # Mettre à jour le badge d'anomalie
        anomalie = cas.get('anomalie', 'N/A')
        self.anomaly_badge.setText(f"🚨 {anomalie}")
        
        # Couleur du badge selon le type d'anomalie
        if "profil" in anomalie.lower():
            badge_color = "#ff9800"
        elif "direction" in anomalie.lower():
            badge_color = "#2196f3"
        elif "non rh" in anomalie.lower():
            badge_color = "#f44336"
        elif "inactif" in anomalie.lower():
            badge_color = "#9c27b0"
        else:
            badge_color = "#607d8b"
        
        self.anomaly_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {badge_color};
                color: #000000;
                font-weight: bold;
                font-size: 13px;
                padding: 12px 16px;
                border-radius: 8px;
                border-left: 4px solid {badge_color}cc;
            }}
        """)
    
    def display_comparison(self, cas):
        """Afficher la comparaison avec design moderne et différences surlignées"""
        # Nettoyer le layout existant
        for i in reversed(range(self.comparison_layout.count())):
            child = self.comparison_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Données de comparaison
        profil_ext = str(cas.get('profil', 'N/A'))
        profil_rh = str(cas.get('profil_rh', 'N/A'))
        direction_ext = str(cas.get('direction', 'N/A'))
        direction_rh = str(cas.get('direction_rh', 'N/A'))
        
        # Créer les sections de comparaison
        if profil_ext != profil_rh:
            self.create_comparison_section("👤 Profil", profil_ext, profil_rh, True)
        
        if direction_ext != direction_rh:
            self.create_comparison_section("🏢 Direction", direction_ext, direction_rh, True)
        
        # Si pas de différences visibles, afficher quand même pour info
        if profil_ext == profil_rh and direction_ext == direction_rh:
            self.create_info_section("ℹ️ Les profils et directions sont identiques dans les deux systèmes.")
    
    def create_comparison_section(self, title, value_ext, value_rh, has_difference):
        """Créer une section de comparaison visuelle optimisée"""
        section = QWidget()
        section.setStyleSheet("""
            QWidget {
                background-color: #0a0a0a;
                border: 1px solid #333;
                border-radius: 8px;
                margin: 3px 0;
            }
        """)
        
        section_layout = QVBoxLayout(section)
        section_layout.setContentsMargins(12, 10, 12, 10)  # Marges réduites
        section_layout.setSpacing(6)  # Espacement réduit
        
        # Titre de la section
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: #0099ff; font-weight: bold; font-size: 13px;
            background: transparent;
        """)
        section_layout.addWidget(title_label)
        
        # Container de comparaison côte-à-côte
        comparison_row = QWidget()
        comparison_layout = QHBoxLayout(comparison_row)
        comparison_layout.setSpacing(10)  # Espacement réduit
        comparison_layout.setContentsMargins(0, 0, 0, 0)
        
        # Colonne Extraction
        ext_container = self.create_value_container(
            "📤 Extraction", value_ext, "#ff9800" if has_difference else "#4caf50"
        )
        comparison_layout.addWidget(ext_container)
        
        # Flèche de comparaison
        arrow_label = QLabel("vs")
        arrow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        arrow_label.setStyleSheet("""
            color: #666; font-weight: bold; font-size: 11px;
            background: transparent; min-width: 25px; max-width: 25px;
        """)
        comparison_layout.addWidget(arrow_label)
        
        # Colonne RH
        rh_container = self.create_value_container(
            "🏛️ RH", value_rh, "#4caf50"
        )
        comparison_layout.addWidget(rh_container)
        
        section_layout.addWidget(comparison_row)
        self.comparison_layout.addWidget(section)
    
    def create_value_container(self, label, value, color):
        """Créer un container pour une valeur avec style optimisé"""
        container = QWidget()
        container.setStyleSheet(f"""
            QWidget {{
                background-color: #0d0d0d;
                border: 2px solid {color}40;
                border-radius: 6px;
                padding: 8px;
            }}
        """)
        
        layout = QVBoxLayout(container)
        layout.setSpacing(3)  # Espacement réduit
        layout.setContentsMargins(6, 6, 6, 6)  # Marges réduites
        
        # Label
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"""
            color: {color}; font-weight: bold; font-size: 10px;
            background: transparent;
        """)
        layout.addWidget(label_widget)
        
        # Valeur
        value_widget = QLabel(value)
        value_widget.setStyleSheet("""
            color: #ffffff; font-size: 12px; font-weight: 500;
            background: transparent; padding: 2px 0;
        """)
        value_widget.setWordWrap(True)
        layout.addWidget(value_widget)
        
        return container
    
    def create_info_section(self, message):
        """Créer une section d'information"""
        info_widget = QLabel(message)
        info_widget.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 15px;
                color: #999;
                font-style: italic;
                text-align: center;
            }
        """)
        info_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_widget.setWordWrap(True)
        self.comparison_layout.addWidget(info_widget)
    
    def show_current_case(self, ext_df):
        """Afficher le cas en cours de validation"""
        self.ext_df = ext_df
        self.cas_a_verifier = extraire_cas_a_verifier(ext_df)
        
        if len(self.cas_a_verifier) == 0:
            self.show_completion_message()
            return
        
        if self.current_cas_index >= len(self.cas_a_verifier):
            self.current_cas_index = 0
        
        self.display_case()
    
    def display_case(self):
        """Afficher les informations du cas actuel"""
        # Compteur et progression
        total_cases = len(self.cas_a_verifier)
        self.validation_counter.setText(f"Cas {self.current_cas_index + 1} sur {total_cases}")
        
        progress = ((self.current_cas_index) / total_cases) * 100 if total_cases > 0 else 0
        self.validation_progress.setValue(int(progress))
        
        # Récupérer le cas actuel
        cas_idx = self.cas_a_verifier.index[self.current_cas_index]
        cas = self.cas_a_verifier.loc[cas_idx]
        
        # S'assurer que les cards sont visibles
        self.anomaly_card.setVisible(True)
        self.actions_card.setVisible(True)
        
        # Afficher les informations
        self.display_case_info(cas)
        self.display_comparison(cas)
        self.configure_actions(cas)
        
        # Réinitialiser le commentaire
        self.comment_edit.clear()
    
    def configure_actions(self, cas):
        """Configurer les actions selon l'anomalie et son type"""
        anomalie = cas.get('anomalie', '')
        type_change = cas.get('type_changement', {})
        
        # Pour les variations d'écriture
        if "Variation" in anomalie:
            self.modifier_container.setVisible(False)  # Pas de modification pour les variations
            self.radio_conserver.setChecked(True)
            # Modifier le texte de l'action
            self.radio_conserver.setText("✓ Confirmer l'équivalence")
        
        # Pour les changements réels
        elif "Changement" in anomalie:
            self.modifier_container.setVisible(True)
            self.radio_modifier.setChecked(True)
            # Texte standard
            self.radio_modifier.setText("✏️ Modifier")
            self.radio_conserver.setText("✓ Conserver")
        
        else:
            # Comportement par défaut
            self.modifier_container.setVisible(False)
            self.radio_conserver.setChecked(True)
            self.radio_conserver.setText("✓ Conserver")
    
    def validate_decision(self):
        """Valider la décision pour le cas en cours"""
        if len(self.cas_a_verifier) == 0:
            return
        
        decision = self.get_selected_decision()
        cas_idx = self.cas_a_verifier.index[self.current_cas_index]
        cas = self.cas_a_verifier.loc[cas_idx]
        
        self.save_decision(cas_idx, decision, cas)
        self.parent_window.show_status_message(f"✅ Décision '{decision}' enregistrée", 2000)
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
        self.ext_df.loc[cas_idx, 'decision_manuelle'] = decision
        
        comment = self.comment_edit.toPlainText().strip()
        if comment:
            self.ext_df.loc[cas_idx, 'comment_certificateur'] = comment
        
        if decision in ["Modifier", "Conserver"]:
            self.add_to_whitelists(cas, decision)
    
    def add_to_whitelists(self, cas, decision):
        """Ajouter aux whitelists si nécessaire"""
        anomalie = cas.get('anomalie', '')
        if "Changement de profil à vérifier" in anomalie:
            ajouter_profil_valide(cas, certificateur=self.parent_window.certificateur)
            if "variation" in anomalie.lower():
                ajouter_variation_profil(cas, self.parent_window.certificateur)
            elif "changement" in anomalie.lower():
                ajouter_changement_profil(cas, self.parent_window.certificateur)
        if "Changement de direction à vérifier" in anomalie:
            ajouter_direction_valide(cas, certificateur=self.parent_window.certificateur)
            if "variation" in anomalie.lower():
                ajouter_variation_direction(cas, self.parent_window.certificateur)
            elif "changement" in anomalie.lower():
                ajouter_changement_direction(cas, self.parent_window.certificateur)
    
    def proceed_to_next_case(self):
        """Passer au cas suivant ou afficher la fin"""
        self.cas_a_verifier = extraire_cas_a_verifier(self.ext_df)
        
        if len(self.cas_a_verifier) > 0:
            self.current_cas_index = 0
            self.display_case()
        else:
            self.show_completion_message()
    
    def skip_case(self):
        """Passer au cas suivant sans décision"""
        self.current_cas_index += 1
        if self.current_cas_index >= len(self.cas_a_verifier):
            self.current_cas_index = 0
        self.display_case()
    
    def show_completion_message(self):
        """Afficher le message de fin de validation"""
        self.validation_counter.setText("✅ Tous les cas traités")
        
        # Masquer les sections anomalie et actions
        self.anomaly_card.setVisible(False)
        self.actions_card.setVisible(False)
        
        # Afficher le bouton de fin
        self.finish_validation_button.setVisible(True)
        
        # Message de completion dans la zone utilisateur
        completion_html = """
        <div style="text-align: center; padding: 20px;">
            <h2 style="color: #00ff55;">🎉 Validation Terminée!</h2>
            <p style="color: #ffffff; font-size: 14px;">
                Tous les cas ont été traités avec succès.<br>
                Vous pouvez maintenant générer le rapport final.
            </p>
        </div>
        """
        self.user_info_label.setText(completion_html)
        
        # Nettoyer la zone de comparaison
        for i in reversed(range(self.comparison_layout.count())):
            child = self.comparison_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        self.create_info_section("✅ Tous les cas ont été traités avec succès!")

    
    def reset_page(self):
        """Réinitialiser la page"""
        self.current_cas_index = 0
        self.validation_counter.setText("")
        self.user_info_label.setText("")
        self.comment_edit.clear()
        self.validation_progress.setValue(0)
        self.finish_validation_button.setVisible(False)
        
        # Rendre les cards visibles à nouveau
        self.anomaly_card.setVisible(True)
        self.actions_card.setVisible(True)

    def set_data(self, df, certificateur):
        self.df = df
        self.certificateur = certificateur
        self.update_table()
        
    def update_table(self):
        if self.df is None:
            return
            
        self.table.setRowCount(0)
        
        for _, row in self.df.iterrows():
            if row['cas_automatique']:
                continue
                
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            
            # Récupérer les types de changements
            type_change = row.get('type_changement', {})
            type_profil = type_change.get('profil', '')
            type_direction = type_change.get('direction', '')
            
            # Créer l'item de type de changement
            type_text = []
            if type_profil:
                type_text.append(f"Profil: {type_profil}")
            if type_direction:
                type_text.append(f"Direction: {type_direction}")
            type_item = QTableWidgetItem(" | ".join(type_text))
            
            # Appliquer le style selon le type
            if 'variation' in type_text:
                type_item.setBackground(QColor(255, 255, 200))  # Jaune clair
            elif 'changement' in type_text:
                type_item.setBackground(QColor(255, 200, 200))  # Rouge clair
            
            self.table.setItem(row_position, 0, QTableWidgetItem(str(row.get('utilisateur', ''))))
            self.table.setItem(row_position, 1, QTableWidgetItem(str(row.get('profil', ''))))
            self.table.setItem(row_position, 2, QTableWidgetItem(str(row.get('profil_rh', ''))))
            self.table.setItem(row_position, 3, QTableWidgetItem(str(row.get('direction', ''))))
            self.table.setItem(row_position, 4, QTableWidgetItem(str(row.get('direction_rh', ''))))
            self.table.setItem(row_position, 5, type_item)
            
            decision_combo = QComboBox()
            decision_combo.addItems(["", "Conserver", "Désactiver"])
            if row.get('decision_manuelle'):
                decision_combo.setCurrentText(row['decision_manuelle'])
            decision_combo.currentTextChanged.connect(
                lambda text, r=row: self.on_decision_changed(r, text)
            )
            self.table.setCellWidget(row_position, 6, decision_combo)
            
    def apply_filters(self):
        if self.df is None:
            return
            
        filter_type = self.filter_combo.currentText()
        search_text = self.search_input.text().lower()
        
        for row in range(self.table.rowCount()):
            show_row = True
            
            # Filtre par type
            if filter_type != "Tous":
                type_item = self.table.item(row, 5)
                if type_item:
                    type_text = type_item.text().lower()
                    if filter_type == "Variations" and "variation" not in type_text:
                        show_row = False
                    elif filter_type == "Changements" and "changement" not in type_text:
                        show_row = False
            
            # Filtre par recherche
            if show_row and search_text:
                found = False
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item and search_text in item.text().lower():
                        found = True
                        break
                show_row = found
            
            self.table.setRowHidden(row, not show_row)
            
    def on_decision_changed(self, row, decision):
        if not decision:
            return
            
        # Mettre à jour la décision dans le DataFrame
        mask = (self.df['utilisateur'] == row['utilisateur'])
        self.df.loc[mask, 'decision_manuelle'] = decision
        
        # Ajouter aux profils/directions valides selon le type
        type_change = row.get('type_changement', {})
        
        if type_change.get('profil') == 'variation':
            ajouter_variation_profil(row, self.certificateur)
        elif type_change.get('profil') == 'changement':
            ajouter_changement_profil(row, self.certificateur)
            
        if type_change.get('direction') == 'variation':
            ajouter_variation_direction(row, self.certificateur)
        elif type_change.get('direction') == 'changement':
            ajouter_changement_direction(row, self.certificateur)
            
    def validate_selection(self):
        if self.df is None:
            return
            
        # Vérifier que toutes les décisions sont prises
        pending = self.df[
            (~self.df['cas_automatique']) & 
            (self.df['decision_manuelle'] == "")
        ]
        
        if not pending.empty:
            QMessageBox.warning(
                self,
                "Décisions manquantes",
                "Veuillez prendre une décision pour tous les cas avant de valider."
            )
            return
            
        # Mettre à jour les décisions finales
        self.df['decision_finale'] = self.df['decision_manuelle']
        self.df.loc[self.df['cas_automatique'], 'decision_finale'] = self.df.loc[
            self.df['cas_automatique'], 'decision_manuelle'
        ]
        
        QMessageBox.information(
            self,
            "Validation réussie",
            "Les décisions ont été enregistrées avec succès."
        )
        
    def generate_report(self):
        if self.df is None:
            return
            
        # Vérifier que toutes les décisions sont prises
        if 'decision_finale' not in self.df.columns:
            QMessageBox.warning(
                self,
                "Décisions manquantes",
                "Veuillez valider les décisions avant de générer le rapport."
            )
            return
            
        # Demander l'emplacement du fichier
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer le rapport",
            "",
            "Excel Files (*.xlsx);;All Files (*)"
        )
        
        if file_path:
            try:
                generer_rapport(self.df, file_path)
                QMessageBox.information(
                    self,
                    "Rapport généré",
                    f"Le rapport a été généré avec succès :\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    f"Erreur lors de la génération du rapport :\n{str(e)}"
                )
                
    def on_back_clicked(self):
        # Vérifier s'il y a des décisions non prises
        if self.df is not None:
            pending = self.df[
                (~self.df['cas_automatique']) & 
                (self.df['decision_manuelle'] == "")
            ]
            
            if not pending.empty:
                reply = QMessageBox.question(
                    self,
                    "Décisions non prises",
                    "Il reste des décisions à prendre. Voulez-vous vraiment quitter ?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.No:
                    return
                    
        self.back_clicked.emit()
        
    def reset_page(self):
        self.df = None
        self.certificateur = None
        self.table.setRowCount(0)
        self.filter_combo.setCurrentText("Tous")
        self.search_input.clear()