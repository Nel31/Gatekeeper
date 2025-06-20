"""
Page d'affichage des anomalies (Étape 2) - Version compacte et responsive
Thème rouge bordeaux, noir et blanc
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QTableWidget, QTableWidgetItem, QLineEdit, 
                            QComboBox, QHeaderView, QSizePolicy, QButtonGroup, QMessageBox, QFileDialog)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, pyqtSignal

from ui.widgets.stat_widget import StatWidget
from core.anomalies import extraire_cas_a_verifier, extraire_cas_automatiques
from core.report import generer_rapport
from mapping.profils_valides import (
    ajouter_profil_valide, ajouter_variation_profil, ajouter_changement_profil
)
from mapping.directions_conservees import (
    ajouter_direction_valide, ajouter_variation_direction, ajouter_changement_direction
)


class AnomaliesPage(QWidget):
    """Page d'affichage des anomalies - Version ultra-compacte avec thème rouge bordeaux"""
    
    back_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.current_view = "manual"  # manual, auto, validated
        self.df = None
        self.certificateur = None
        self.setup_ui()
    
    def setup_ui(self):
        """Configurer l'interface compacte"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)  # Marges réduites
        layout.setSpacing(8)  # Espacement minimal
        
        # Header ultra-compact
        self.create_compact_header(layout)
        
        # Statistiques compactes
        self.create_compact_stats(layout)
        
        # Barre de contrôles (filtres + recherche)
        self.create_control_bar(layout)
        
        # Tableau unique responsive
        self.create_single_table(layout)
        
        # Navigation minimaliste
        self.create_compact_navigation(layout)
    
    def create_compact_header(self, parent_layout):
        """Header ultra-compact sur une seule ligne - Thème rouge bordeaux"""
        header_container = QWidget()
        header_container.setFixedHeight(50)  # Hauteur fixe réduite
        header_container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #220000, stop:1 #000000);
                border-radius: 8px;
            }
        """)
        
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(15, 8, 15, 8)
        
        # Titre compact
        title = QLabel("🔍 Anomalies Détectées")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff; background: transparent;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Badge de statut compact - rouge bordeaux
        self.status_badge = QLabel("En analyse")
        self.status_badge.setStyleSheet("""
            QLabel {
                background-color: #800020;
                color: white;
                padding: 6px 12px;
                border-radius: 15px;
                font-weight: bold;
                font-size: 11px;
            }
        """)
        header_layout.addWidget(self.status_badge)
        
        parent_layout.addWidget(header_container)
    
    def create_compact_stats(self, parent_layout):
        """Statistiques compactes et responsives - Thème rouge bordeaux"""
        stats_container = QWidget()
        stats_container.setFixedHeight(60)  # Hauteur réduite
        stats_container.setStyleSheet("""
            QWidget {
                background-color: #0a0a0a;
                border: 1px solid #1a1a1a;
                border-radius: 8px;
            }
        """)
        
        stats_layout = QHBoxLayout(stats_container)
        stats_layout.setContentsMargins(10, 5, 10, 5)
        stats_layout.setSpacing(8)
        
        # Stats compactes avec couleurs du thème rouge
        self.create_compact_stat_widget("Total", "0", "#B22222", stats_layout)
        self.create_compact_stat_widget("Anomalies", "0", "#FF9800", stats_layout)
        self.create_compact_stat_widget("À vérifier", "0", "#800020", stats_layout)
        self.create_compact_stat_widget("Auto", "0", "#A52A2A", stats_layout)
        self.create_compact_stat_widget("Conformes", "0", "#4CAF50", stats_layout)
        
        parent_layout.addWidget(stats_container)
    
    def create_compact_stat_widget(self, label, value, color, parent_layout):
        """Widget de statistique ultra-compact"""
        stat_widget = QWidget()
        stat_widget.setFixedSize(90, 45)  # Taille fixe réduite
        stat_widget.setStyleSheet(f"""
            QWidget {{
                background-color: #0d0d0d;
                border: 1px solid {color};
                border-radius: 6px;
            }}
        """)
        
        layout = QVBoxLayout(stat_widget)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(0)
        
        # Valeur
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet(f"color: {color}; background: transparent;")
        layout.addWidget(value_label)
        
        # Label
        text_label = QLabel(label)
        text_label.setFont(QFont("Arial", 9))
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setStyleSheet("color: #ccc; background: transparent;")
        layout.addWidget(text_label)
        
        # Stocker la référence pour mise à jour
        setattr(self, f"stat_{label.lower().replace(' ', '_').replace('à_', 'a_')}", value_label)
        
        parent_layout.addWidget(stat_widget)
    
    def create_control_bar(self, parent_layout):
        """Barre de contrôles compacte - Thème rouge bordeaux"""
        control_container = QWidget()
        control_container.setFixedHeight(40)
        control_layout = QHBoxLayout(control_container)
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(10)
        
        # Boutons de filtrage (remplacent les tabs)
        self.create_filter_buttons(control_layout)
        
        # Séparateur visuel
        separator = QLabel("|")
        separator.setStyleSheet("color: #333; font-size: 20px;")
        control_layout.addWidget(separator)
        
        # Recherche compacte
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher...")
        self.search_input.setFixedHeight(32)
        self.search_input.setMaximumWidth(200)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #0d0d0d;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                color: #fff;
            }
            QLineEdit:focus { border: 2px solid #800020; }
        """)
        self.search_input.textChanged.connect(self.filter_table)
        control_layout.addWidget(self.search_input)
        
        # Filtre par anomalie compact
        self.anomaly_filter = QComboBox()
        self.anomaly_filter.addItems([
            "Toutes", "Non RH", "Profil", "Direction", "Inactif"
        ])
        self.anomaly_filter.setFixedHeight(32)
        self.anomaly_filter.setMaximumWidth(120)
        self.anomaly_filter.setStyleSheet("""
            QComboBox {
                background-color: #0d0d0d;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 6px 8px;
                font-size: 12px;
                color: #fff;
            }
        """)
        self.anomaly_filter.currentTextChanged.connect(self.filter_table)
        control_layout.addWidget(self.anomaly_filter)
        
        control_layout.addStretch()
        
        parent_layout.addWidget(control_container)
    
    def create_filter_buttons(self, parent_layout):
        """Boutons de filtrage élégants - Thème rouge bordeaux"""
        self.filter_group = QButtonGroup()
        
        filters = [
            ("manual", "⚠️ À vérifier", "#800020"),    # Rouge bordeaux
            ("auto", "🤖 Auto", "#A52A2A"),           # Rouge bordeaux clair
            ("validated", "✅ Conformes", "#4CAF50")   # Vert conservé
        ]
        
        for filter_id, label, color in filters:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setFixedHeight(32)
            btn.setMinimumWidth(100)
            
            # Style moderne pour les boutons
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #0d0d0d;
                    border: 1px solid {color};
                    border-radius: 6px;
                    padding: 6px 12px;
                    color: {color};
                    font-weight: 600;
                    font-size: 12px;
                }}
                QPushButton:checked {{
                    background-color: {color};
                    color: #000;
                }}
                QPushButton:hover:!checked {{
                    background-color: #1a1a1a;
                    color: #fff;
                }}
            """)
            
            btn.clicked.connect(lambda checked, fid=filter_id: self.switch_view(fid))
            self.filter_group.addButton(btn)
            parent_layout.addWidget(btn)
            
            # Définir le bouton par défaut
            if filter_id == "manual":
                btn.setChecked(True)
    
    def create_single_table(self, parent_layout):
        """Tableau unique qui change de contenu selon le filtre"""
        self.main_table = QTableWidget()
        self.main_table.setStyleSheet("""
            QTableWidget {
                background-color: #0d0d0d;
                border: 1px solid #1a1a1a;
                border-radius: 8px;
                gridline-color: #1a1a1a;
                color: #fff;
                alternate-background-color: #0a0a0a;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
                border-bottom: 1px solid #1a1a1a;
            }
            QHeaderView::section {
                background-color: #0a0a0a;
                border: none;
                border-bottom: 2px solid #800020;
                padding: 10px 8px;
                font-weight: bold;
                color: #fff;
                font-size: 11px;
            }
        """)
        
        self.main_table.setAlternatingRowColors(True)
        self.main_table.setSortingEnabled(True)
        self.main_table.verticalHeader().setVisible(False)
        self.main_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        parent_layout.addWidget(self.main_table)
    
    def create_compact_navigation(self, parent_layout):
        """Navigation ultra-compacte - Thème rouge bordeaux"""
        nav_container = QWidget()
        nav_container.setFixedHeight(45)
        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 5, 0, 5)
        
        self.back_button = QPushButton("← Retour")
        self.back_button.setFixedHeight(35)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 8px 16px;
                color: #ccc;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #333; color: #fff; }
        """)
        self.back_button.clicked.connect(self.on_back_clicked)
        nav_layout.addWidget(self.back_button)
        
        nav_layout.addStretch()
        
        self.validation_button = QPushButton("Validation détaillée →")
        self.validation_button.setFixedHeight(35)
        self.validation_button.setStyleSheet("""
            QPushButton {
                background-color: #800020;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                color: white;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #A52A2A; }
        """)
        self.validation_button.clicked.connect(lambda: self.parent_window.go_to_step(2))
        nav_layout.addWidget(self.validation_button)
        
        parent_layout.addWidget(nav_container)
    
    def switch_view(self, view_type):
        """Changer la vue du tableau"""
        self.current_view = view_type
        self.update_table_content()
        
        # Mettre à jour le message d'information
        self.update_info_message()
    
    def update_table_content(self):
        """Mettre à jour le contenu du tableau selon la vue active"""
        if not hasattr(self, 'ext_df'):
            return
            
        if self.current_view == "manual":
            data = self.cas_a_verifier
            headers = ["Code", "Nom/Prénom", "Anomalie", "Profil RH", "Direction RH", "Inactivité"]
            self.fill_manual_data(data, headers)
        elif self.current_view == "auto":
            data = extraire_cas_automatiques(self.ext_df)
            headers = ["Code", "Nom/Prénom", "Type", "Profil RH", "Direction RH", "Décision"]
            self.fill_auto_data(data, headers)
        else:  # validated
            data = self.extraire_comptes_valides(self.ext_df)
            headers = ["Code", "Nom/Prénom", "Profil", "Direction"]
            self.fill_validated_data(data, headers)
    
    def fill_manual_data(self, data, headers):
        """Remplir le tableau - Toujours afficher valeurs RH - Couleurs thème rouge"""
        self.main_table.setRowCount(len(data))
        self.main_table.setColumnCount(len(headers))
        self.main_table.setHorizontalHeaderLabels(headers)
        
        for i, (idx, row) in enumerate(data.iterrows()):
            self.main_table.setItem(i, 0, self.create_styled_item(str(row['code_utilisateur']), "#B22222"))
            self.main_table.setItem(i, 1, self.create_styled_item(str(row['nom_prenom'])))
            
            # Anomalie avec indicateur visuel
            anomalie_text = str(row['anomalie'])
            if "harmonisé" in anomalie_text.lower():
                # Jamais affiché dans cas manuels car auto-géré
                pass
            else:
                self.main_table.setItem(i, 2, self.create_styled_item(anomalie_text, "#ff9900"))
            
            # Toujours afficher valeurs RH
            self.main_table.setItem(i, 3, self.create_styled_item(str(row.get('profil_rh', 'N/A'))))
            self.main_table.setItem(i, 4, self.create_styled_item(str(row.get('direction_rh', 'N/A'))))
            
            # Inactivité
            jours = row.get('days_inactive', 'N/A')
            jours_text = f"{jours:.0f}j" if isinstance(jours, (int, float)) else str(jours)
            color = "#ff5555" if isinstance(jours, (int, float)) and jours > 120 else None
            self.main_table.setItem(i, 5, self.create_styled_item(jours_text, color))
        
        self.adjust_table_columns()
    
    def fill_auto_data(self, data, headers):
        """Remplir les cas automatiques avec distinction visuelle - Couleurs thème rouge"""
        self.main_table.setRowCount(len(data))
        self.main_table.setColumnCount(len(headers))
        self.main_table.setHorizontalHeaderLabels(headers)
        
        for i, (idx, row) in enumerate(data.iterrows()):
            self.main_table.setItem(i, 0, self.create_styled_item(str(row['code_utilisateur']), "#B22222"))
            self.main_table.setItem(i, 1, self.create_styled_item(str(row['nom_prenom'])))
            
            # Type d'automatisation
            anomalie = str(row['anomalie'])
            if "harmonisé" in anomalie.lower():
                type_text = "↻ Harmonisation"
                color = "#4CAF50"
            elif "non rh" in anomalie.lower():
                type_text = "🚫 Non RH"
                color = "#F44336"
            elif "inactif" in anomalie.lower():
                type_text = "💤 Inactivité"
                color = "#A52A2A"  # Rouge bordeaux clair
            else:
                type_text = "✓ Validé"
                color = "#800020"  # Rouge bordeaux
            
            self.main_table.setItem(i, 2, self.create_styled_item(type_text, color))
            
            # Valeurs RH
            self.main_table.setItem(i, 3, self.create_styled_item(str(row.get('profil_rh', 'N/A'))))
            self.main_table.setItem(i, 4, self.create_styled_item(str(row.get('direction_rh', 'N/A'))))
            
            # Décision
            self.main_table.setItem(i, 5, self.create_styled_item(row.get('decision_manuelle', ''), "#00ff55"))
        
        self.adjust_table_columns()
    
    def fill_validated_data(self, data, headers):
        """Remplir avec les données validées"""
        self.main_table.setRowCount(len(data))
        self.main_table.setColumnCount(len(headers))
        self.main_table.setHorizontalHeaderLabels(headers)
        
        for i, (idx, row) in enumerate(data.iterrows()):
            self.main_table.setItem(i, 0, self.create_styled_item(str(row['code_utilisateur']), "#B22222"))
            self.main_table.setItem(i, 1, self.create_styled_item(str(row['nom_prenom'])))
            self.main_table.setItem(i, 2, self.create_styled_item(str(row.get('profil', 'N/A'))))
            self.main_table.setItem(i, 3, self.create_styled_item(str(row.get('direction', 'N/A'))))
        
        self.adjust_table_columns()
    
    def create_styled_item(self, text, color=None):
        """Créer un item stylé"""
        item = QTableWidgetItem(text)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        if color:
            item.setForeground(QColor(color))
        return item
    
    def create_comparison_item(self, text, is_different):
        """Créer un item de comparaison"""
        item = QTableWidgetItem(text)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        
        if is_different:
            item.setBackground(QColor("#330000"))
            item.setForeground(QColor("#ff9999"))
        else:
            item.setForeground(QColor("#99ff99"))
        
        return item
    
    def adjust_table_columns(self):
        """Ajuster les colonnes de manière responsive"""
        header = self.main_table.horizontalHeader()
        
        # Colonnes fixes pour les codes et noms
        if self.main_table.columnCount() > 0:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        if self.main_table.columnCount() > 1:
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        
        # Autres colonnes en mode stretch
        for i in range(2, self.main_table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
    
    def update_page(self, ext_df):
        """Mettre à jour la page - Afficher les vraies statistiques"""
        self.ext_df = ext_df
        
        # Compter les différents types
        harmonisations = len(ext_df[ext_df['anomalie'].str.contains('harmonisé', case=False, na=False)])
        changements_reels = len(ext_df[ext_df['anomalie'].str.contains('Changement.*vérifier', case=False, na=False)])
        
        # Extraire les données
        cas_automatiques = extraire_cas_automatiques(ext_df)
        self.cas_a_verifier = extraire_cas_a_verifier(ext_df)
        comptes_valides = self.extraire_comptes_valides(ext_df)
        
        # Mettre à jour les statistiques avec distinction
        total = len(ext_df)
        anomalies = len(ext_df[ext_df['anomalie'].str.len() > 0])
        manual = len(self.cas_a_verifier)
        auto = len(cas_automatiques)
        validated = len(comptes_valides)
        
        self.stat_total.setText(str(total))
        self.stat_anomalies.setText(f"{anomalies} ({harmonisations}↻)")  # Symbole pour harmonisations
        self.stat_a_vérifier.setText(str(manual))
        self.stat_auto.setText(str(auto))
        self.stat_conformes.setText(str(validated))
        
        # Badge modifié - couleurs thème rouge
        if manual == 0:
            self.status_badge.setText("✅ Complet")
            self.status_badge.setStyleSheet(self.status_badge.styleSheet().replace("#800020", "#00cc44"))
        else:
            self.status_badge.setText(f"⚠️ {manual} changements réels")
        
        self.update_table_content()
    
    def extraire_comptes_valides(self, ext_df):
        """Extraire les comptes sans anomalies"""
        return ext_df[
            (ext_df['anomalie'].str.len() == 0) | 
            (ext_df['anomalie'].isna())
        ]
    
    def filter_table(self):
        """Filtrer le tableau selon la recherche et le filtre"""
        search_text = self.search_input.text().lower()
        anomaly_filter = self.anomaly_filter.currentText()
        
        # Implémentation basique du filtrage
        for row in range(self.main_table.rowCount()):
            show_row = True
            
            # Filtre par recherche
            if search_text:
                row_text = ""
                for col in range(min(3, self.main_table.columnCount())):  # Chercher dans les 3 premières colonnes
                    item = self.main_table.item(row, col)
                    if item:
                        row_text += item.text().lower() + " "
                
                if search_text not in row_text:
                    show_row = False
            
            # Filtre par type d'anomalie
            if show_row and anomaly_filter != "Toutes" and self.main_table.columnCount() > 2:
                anomaly_item = self.main_table.item(row, 2)  # Colonne anomalie
                if anomaly_item:
                    anomaly_text = anomaly_item.text()
                    filter_map = {
                        "Non RH": "non rh",
                        "Profil": "profil",
                        "Direction": "direction",
                        "Inactif": "inactif"
                    }
                    if anomaly_filter in filter_map:
                        if filter_map[anomaly_filter] not in anomaly_text.lower():
                            show_row = False
            
            self.main_table.setRowHidden(row, not show_row)
    
    def update_info_message(self):
        """Mettre à jour le message d'information selon la vue"""
        # Cette méthode peut être étendue pour afficher des messages contextuels
        pass

    def reset_page(self):
        """Réinitialiser la page des anomalies"""
        # Réinitialiser les données
        if hasattr(self, 'ext_df'):
            del self.ext_df
        if hasattr(self, 'cas_a_verifier'):
            del self.cas_a_verifier
        
        # Vider le tableau
        self.main_table.setRowCount(0)
        self.main_table.setColumnCount(0)
        
        # Réinitialiser les statistiques
        self.stat_total.setText("0")
        self.stat_anomalies.setText("0")
        self.stat_a_vérifier.setText("0")
        self.stat_auto.setText("0")
        self.stat_conformes.setText("0")
        
        # Réinitialiser les filtres
        self.search_input.clear()
        self.anomaly_filter.setCurrentIndex(0)
        
        # Réinitialiser le badge - couleur rouge bordeaux
        self.status_badge.setText("En analyse")
        self.status_badge.setStyleSheet("""
            QLabel {
                background-color: #800020;
                color: white;
                padding: 6px 12px;
                border-radius: 15px;
                font-weight: bold;
                font-size: 11px;
            }
        """)
        
        # Réinitialiser la vue
        self.current_view = "manual"
        # Cocher le bouton "À vérifier"
        for button in self.filter_group.buttons():
            if "À vérifier" in button.text():
                button.setChecked(True)
                break

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