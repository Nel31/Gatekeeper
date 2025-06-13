"""
Page d'affichage des anomalies (Étape 2)
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QTableWidget, QTableWidgetItem, QGroupBox,
                            QComboBox, QTabWidget, QHeaderView, QMessageBox, QSizePolicy)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt

from ui.widgets.stat_widget import StatWidget
from ui.styles import INFO_MESSAGE_STYLE, AUTO_MESSAGE_STYLE, COMBO_BOX_STYLE
from ui.utils import show_decision_help_dialog, show_question_message
from core.anomalies import extraire_cas_a_verifier, extraire_cas_automatiques, compter_anomalies_par_type
from mapping.profils_valides import ajouter_profil_valide
from mapping.directions_conservees import ajouter_direction_conservee


class AnomaliesPage(QWidget):
    """Page d'affichage des anomalies"""
    
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
        
        # Statistiques
        self.create_stats_section(layout)
        
        # Répartition des anomalies
        #self.create_anomalies_summary_section(layout)
        
        # Tabs pour les cas
        self.create_tabs_section(layout)
        
        # Boutons de navigation
        self.create_navigation_buttons(layout)
    
    def create_title_section(self, parent_layout):
        """Créer la section titre"""
        title = QLabel("🔍 Anomalies détectées")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        parent_layout.addWidget(title)
    
    def create_stats_section(self, parent_layout):
        """Créer la section statistiques"""
        self.stats_widget = QWidget()
        self.stats_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.stats_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        stats_layout = QHBoxLayout(self.stats_widget)
        
        self.stat_total = StatWidget("Total comptes", "0", "#2196F3")
        self.stat_validated = StatWidget("Validés", "0", "#4CAF50")
        self.stat_anomalies = StatWidget("Avec anomalies", "0", "#FF9800")
        self.stat_manual = StatWidget("À vérifier", "0", "#F44336")
        self.stat_auto = StatWidget("Auto traités", "0", "#9C27B0")
        
        stats_layout.addWidget(self.stat_total)
        stats_layout.addWidget(self.stat_validated)
        stats_layout.addWidget(self.stat_anomalies)
        stats_layout.addWidget(self.stat_manual)
        stats_layout.addWidget(self.stat_auto)
        
        parent_layout.addWidget(self.stats_widget)
    
    def create_anomalies_summary_section(self, parent_layout):
        """Créer la section résumé des anomalies"""
        anomalies_summary = QGroupBox("Répartition des anomalies")
        anomalies_layout = QVBoxLayout()
        self.anomalies_summary_label = QLabel()
        anomalies_layout.addWidget(self.anomalies_summary_label)
        anomalies_summary.setLayout(anomalies_layout)
        parent_layout.addWidget(anomalies_summary)
    
    def create_tabs_section(self, parent_layout):
        """Créer la section avec les onglets"""
        self.anomalies_tabs = QTabWidget()
        self.anomalies_tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Tab 1: Cas manuels
        self.create_manual_tab()
        
        # Tab 2: Cas automatiques
        self.create_auto_tab()
        
        # Tab 3: Comptes validés (sans anomalies)
        self.create_validated_tab()
        
        parent_layout.addWidget(self.anomalies_tabs)
    
    def create_manual_tab(self):
        """Créer l'onglet des cas manuels"""
        manual_tab = QWidget()
        manual_tab.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        manual_layout = QVBoxLayout(manual_tab)
        
        # Message informatif
        info_label = QLabel("💡 Vous pouvez prendre les décisions directement dans le tableau ci-dessous en utilisant les menus déroulants.")
        info_label.setStyleSheet(INFO_MESSAGE_STYLE)
        info_label.setWordWrap(True)
        manual_layout.addWidget(info_label)
        
        # Barre d'outils
        self.create_toolbar(manual_layout)
        
        # Tableau des cas manuels
        self.manual_table = QTableWidget()
        self.manual_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.manual_table.setAlternatingRowColors(True)
        self.manual_table.setSortingEnabled(True)
        self.manual_table.verticalHeader().setDefaultSectionSize(40)
        manual_layout.addWidget(self.manual_table)
        
        self.anomalies_tabs.addTab(manual_tab, "🔍 Cas à vérifier manuellement")
    
    def create_auto_tab(self):
        """Créer l'onglet des cas automatiques"""
        auto_tab = QWidget()
        auto_tab.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        auto_layout = QVBoxLayout(auto_tab)
        
        # Info sur les cas automatiques
        auto_info = QLabel("ℹ️ Ces cas ont été traités automatiquement selon les règles définies (inactivité > 120 jours, profils/directions whitelistés).")
        auto_info.setStyleSheet(AUTO_MESSAGE_STYLE)
        auto_info.setWordWrap(True)
        auto_layout.addWidget(auto_info)
        
        # Tableau des cas automatiques
        self.auto_table = QTableWidget()
        self.auto_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.auto_table.setAlternatingRowColors(True)
        self.auto_table.setSortingEnabled(True)
        self.auto_table.verticalHeader().setDefaultSectionSize(40)
        auto_layout.addWidget(self.auto_table)
        
        self.anomalies_tabs.addTab(auto_tab, "✅ Cas traités automatiquement")
    
    def create_validated_tab(self):
        """Créer l'onglet des comptes validés (sans anomalies)"""
        validated_tab = QWidget()
        validated_tab.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        validated_layout = QVBoxLayout(validated_tab)
        
        # Info sur les comptes validés
        validated_info = QLabel("✅ Ces comptes sont conformes et ne présentent aucune anomalie. Ils sont automatiquement conservés.")
        validated_info.setStyleSheet("""
            QLabel {
                background-color: #e8f5e9;
                border: 1px solid #c8e6c9;
                border-radius: 4px;
                padding: 10px;
                color: #1b5e20;
                font-size: 13px;
            }
        """)
        validated_info.setWordWrap(True)
        validated_layout.addWidget(validated_info)
        
        # Tableau des comptes validés
        self.validated_table = QTableWidget()
        self.validated_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.validated_table.setAlternatingRowColors(True)
        self.validated_table.setSortingEnabled(True)
        self.validated_table.verticalHeader().setDefaultSectionSize(40)
        validated_layout.addWidget(self.validated_table)
        
        self.anomalies_tabs.addTab(validated_tab, "✅ Comptes validés")
    
    def create_toolbar(self, parent_layout):
        """Créer la barre d'outils pour les actions groupées"""
        toolbar_layout = QHBoxLayout()
        
        self.select_all_combo = QComboBox()
        self.select_all_combo.addItems(["Actions groupées...", "Tout désactiver", "Tout conserver", "Réinitialiser"])
        self.select_all_combo.currentIndexChanged.connect(self.on_bulk_action)
        self.select_all_combo.setMinimumWidth(150)
        toolbar_layout.addWidget(QLabel("Actions en masse:"))
        toolbar_layout.addWidget(self.select_all_combo)
        
        toolbar_layout.addStretch()
        
        # Légende des couleurs
        self.create_color_legend(toolbar_layout)
        
        # Bouton d'aide rapide
        help_button = QPushButton("💡 Aide")
        help_button.clicked.connect(lambda: show_decision_help_dialog(self))
        toolbar_layout.addWidget(help_button)
        
        parent_layout.addLayout(toolbar_layout)
    
    def create_color_legend(self, parent_layout):
        """Créer la légende des couleurs"""
        legend_widget = QWidget()
        legend_layout = QHBoxLayout(legend_widget)
        legend_layout.setSpacing(15)
        
        # Conserver
        conserv_label = QLabel("■ Conserver")
        conserv_label.setStyleSheet("color: #00ff55; font-weight: bold;")  # Vert clair
        legend_layout.addWidget(conserv_label)
        
        # Modifier
        modif_label = QLabel("■ Modifier")
        modif_label.setStyleSheet("color: #ffaa00; font-weight: bold;")  # Orange clair
        legend_layout.addWidget(modif_label)
        
        # Désactiver
        desact_label = QLabel("■ Désactiver")
        desact_label.setStyleSheet("color: #ff5555; font-weight: bold;")  # Rouge clair
        legend_layout.addWidget(desact_label)
        
        parent_layout.addWidget(legend_widget)
    
    def create_navigation_buttons(self, parent_layout):
        """Créer les boutons de navigation"""
        button_layout = QHBoxLayout()
        self.back_button = QPushButton("← Retour")
        self.back_button.clicked.connect(lambda: self.parent_window.go_to_step(0))
        button_layout.addWidget(self.back_button)
        
        button_layout.addStretch()
        
        self.next_button = QPushButton("Passer à la validation →")
        self.next_button.setObjectName("primaryButton")
        self.next_button.clicked.connect(lambda: self.parent_window.go_to_step(2))
        self.next_button.setToolTip("Vous pouvez prendre les décisions directement dans le tableau ci-dessus ou passer à la validation détaillée")
        button_layout.addWidget(self.next_button)
        
        parent_layout.addLayout(button_layout)
    
    def update_page(self, ext_df):
        """Mettre à jour la page avec les nouvelles données"""
        self.ext_df = ext_df
        
        # Extraire les différents types de cas
        cas_automatiques = extraire_cas_automatiques(ext_df)
        self.cas_a_verifier = extraire_cas_a_verifier(ext_df)
        comptes_valides = self.extraire_comptes_valides(ext_df)
        
        # Statistiques
        total = len(ext_df)
        validated = len(comptes_valides)
        anomalies = len(ext_df[ext_df['anomalie'].str.len() > 0])
        manual = len(self.cas_a_verifier)
        auto = len(cas_automatiques)
        
        self.stat_total.set_value(str(total))
        self.stat_validated.set_value(str(validated))
        self.stat_anomalies.set_value(str(anomalies))
        self.stat_manual.set_value(str(manual))
        self.stat_auto.set_value(str(auto))
        
        # Résumé des anomalies
        #self.update_anomalies_summary(ext_df)
        
        # Remplir les tableaux
        self.fill_manual_table()
        self.fill_auto_table(cas_automatiques)
        self.fill_validated_table(comptes_valides)
        
        # Mettre à jour les badges des tabs
        self.anomalies_tabs.setTabText(0, f"🔍 Cas à vérifier manuellement ({manual})")
        self.anomalies_tabs.setTabText(1, f"⚙️ Cas traités automatiquement ({auto})")
        self.anomalies_tabs.setTabText(2, f"✅ Comptes validés ({validated})")
        
        # Configurer le bouton suivant
        self.configure_next_button(manual)
    
    def update_anomalies_summary(self, ext_df):
        """Mettre à jour le résumé des anomalies"""
        anomalies_count = compter_anomalies_par_type(ext_df)
        
        if anomalies_count:
            summary_text = "Distribution:\n"
            for anomalie, count in sorted(anomalies_count.items(), key=lambda x: x[1], reverse=True):
                summary_text += f"• {anomalie}: {count} cas\n"
            self.anomalies_summary_label.setText(summary_text)
    
    def configure_next_button(self, manual_count):
        """Configurer le bouton suivant selon le nombre de cas manuels"""
        all_manual_decided = manual_count == 0
        
        if all_manual_decided:
            self.next_button.setText("Générer le rapport →")
            try:
                self.next_button.clicked.disconnect()
            except:
                pass
            self.next_button.clicked.connect(lambda: self.parent_window.go_to_step(3))
            
            # Message informatif
            self.parent_window.show_status_message("✅ Toutes les décisions ont été prises ! Vous pouvez générer le rapport.", 5000)
        else:
            self.next_button.setText("Validation manuelle détaillée →")
            try:
                self.next_button.clicked.disconnect()
            except:
                pass
            self.next_button.clicked.connect(lambda: self.parent_window.go_to_step(2))
    
    def fill_manual_table(self):
        """Remplir le tableau des cas manuels"""
        columns = ['code_utilisateur', 'nom_prenom', 'anomalie', 'profil_extraction', 'direction_extraction', 'jours_inactivite', 'decision_manuelle']
        data = self.cas_a_verifier
        
        self.manual_table.setRowCount(len(data))
        self.manual_table.setColumnCount(len(columns))
        self.manual_table.setHorizontalHeaderLabels(
            ['Code utilisateur', 'Nom/Prénom', 'Anomalie', 'Profil extrait', 'Direction extraite', 'Jours inactivité', 'Décision']
        )
        
        # Stocker les indices pour référence
        self.manual_indices = data.index.tolist()
        
        for i, (idx, row) in enumerate(data.iterrows()):
            self.create_table_row(i, idx, row)
        
        # Ajuster les colonnes
        self.adjust_table_columns(self.manual_table)
    
    def create_table_row(self, row_num, idx, row):
        """Créer une ligne du tableau manuel"""
        # Code utilisateur
        item = QTableWidgetItem(str(row['code_utilisateur']))
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.manual_table.setItem(row_num, 0, item)
        
        # Nom/Prénom
        item = QTableWidgetItem(str(row['nom_prenom']))
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.manual_table.setItem(row_num, 1, item)
        
        # Anomalie
        item = QTableWidgetItem(str(row['anomalie']))
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.manual_table.setItem(row_num, 2, item)
        
        # Profil extrait
        item = QTableWidgetItem(str(row.get('profil_extraction', 'N/A')))
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.manual_table.setItem(row_num, 3, item)
        
        # Direction extraite
        item = QTableWidgetItem(str(row.get('direction_extraction', 'N/A')))
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.manual_table.setItem(row_num, 4, item)
        
        # Jours d'inactivité
        item = QTableWidgetItem(str(row.get('jours_inactivite', 'N/A')))
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.manual_table.setItem(row_num, 5, item)
        
        # Décision - ComboBox
        self.create_decision_combo(row_num, idx, row)
    
    def create_decision_combo(self, row_num, idx, row):
        """Créer le combo de décision pour une ligne"""
        combo = QComboBox()
        
        # Déterminer les options selon l'anomalie
        anomalie = row['anomalie']
        if "Changement de profil à vérifier" in anomalie or "Changement de direction à vérifier" in anomalie:
            options = ["", "Modifier", "Conserver", "Désactiver"]
        elif "Compte non RH" in anomalie:
            options = ["", "Conserver", "Désactiver"]
        else:
            options = ["", "Conserver", "Désactiver"]
        
        combo.addItems(options)
        
        # Sélectionner la décision actuelle si elle existe
        current_decision = row.get('decision_manuelle', '')
        if current_decision in options:
            combo.setCurrentText(current_decision)
        
        # Colorer la ligne si une décision est prise
        if current_decision:
            self.color_table_row(row_num, current_decision)
        
        # Connecter le signal de changement
        combo.currentTextChanged.connect(
            lambda text, row_idx=idx, row_n=row_num: self.on_decision_changed(row_idx, text, row_n)
        )
        
        combo.setStyleSheet(COMBO_BOX_STYLE)
        self.manual_table.setCellWidget(row_num, 6, combo)
    
    def color_table_row(self, row_num, decision):
        """Colorer une ligne du tableau selon la décision"""
        if decision == "Conserver":
            color = QColor("#001a00")  # Vert très sombre
        elif decision == "Modifier":
            color = QColor("#1a0f00")  # Orange très sombre
        elif decision == "Désactiver":
            color = QColor("#1a0000")  # Rouge très sombre
        else:
            color = QColor("#0d0d0d")  # Gris très sombre
        
        for col in range(6):
            item = self.manual_table.item(row_num, col)
            if item:
                item.setBackground(color)
    
    def fill_auto_table(self, cas_automatiques):
        """Remplir le tableau des cas automatiques"""
        columns = ['code_utilisateur', 'nom_prenom', 'anomalie', 'profil_extraction', 'direction_extraction', 'jours_inactivite', 'decision_manuelle']
        
        self.auto_table.setRowCount(len(cas_automatiques))
        self.auto_table.setColumnCount(len(columns))
        self.auto_table.setHorizontalHeaderLabels(
            ['Code utilisateur', 'Nom/Prénom', 'Anomalie', 'Profil extrait', 'Direction extraite', 'Jours inactivité', 'Décision automatique']
        )
        
        for i, (idx, row) in enumerate(cas_automatiques.iterrows()):
            self.create_auto_table_row(i, row)
        
        # Ajuster les colonnes
        self.adjust_table_columns(self.auto_table)
    
    def create_auto_table_row(self, row_num, row):
        """Créer une ligne du tableau automatique"""
        # Code utilisateur
        item = QTableWidgetItem(str(row['code_utilisateur']))
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.auto_table.setItem(row_num, 0, item)
        
        # Nom/Prénom
        item = QTableWidgetItem(str(row['nom_prenom']))
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.auto_table.setItem(row_num, 1, item)
        
        # Anomalie
        item = QTableWidgetItem(str(row['anomalie']))
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.auto_table.setItem(row_num, 2, item)
        
        # Profil extrait
        item = QTableWidgetItem(str(row.get('profil_extraction', 'N/A')))
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.auto_table.setItem(row_num, 3, item)
        
        # Direction extraite
        item = QTableWidgetItem(str(row.get('direction_extraction', 'N/A')))
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.auto_table.setItem(row_num, 4, item)
        
        # Jours d'inactivité
        item = QTableWidgetItem(str(row.get('jours_inactivite', 'N/A')))
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.auto_table.setItem(row_num, 5, item)
        
        # Décision (non éditable)
        decision = row.get('decision_manuelle', '')
        item = QTableWidgetItem(decision)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        
        # Colorer selon la décision
        color = self.get_decision_color(decision)
        item.setBackground(color)
        
        if decision == "Conserver":
            item.setForeground(QColor("#00ff55"))  # Vert clair
        elif decision == "Modifier":
            item.setForeground(QColor("#ffaa00"))  # Orange clair
        elif decision == "Désactiver":
            item.setForeground(QColor("#ff5555"))  # Rouge clair

        self.auto_table.setItem(row_num, 6, item)
        
        # Colorer toute la ligne
        for col in range(6):
            self.auto_table.item(row_num, col).setBackground(color)
    
    def get_decision_color(self, decision):
        """Récupérer la couleur selon la décision"""
        if decision == "Conserver":
            return QColor("#001a00")  # Vert très sombre
        elif decision == "Modifier":
            return QColor("#1a0f00")  # Orange très sombre
        elif decision == "Désactiver":
            return QColor("#1a0000")  # Rouge très sombre
        else:
            return QColor("#0d0d0d")  # Gris très sombre par défaut
    
    def adjust_table_columns(self, table):
        """Ajuster les colonnes d'un tableau"""
        col_count = table.columnCount()
        
        if col_count >= 3:
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            
        if col_count >= 4:
            # Pour les tableaux avec 4 colonnes ou plus
            if col_count == 4:
                # Tableau validé : 4 colonnes équilibrées
                table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
            else:
                # Tableau manuel/auto : dernière colonne fixe pour les décisions
                table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
                table.setColumnWidth(3, 150)
    
    def on_decision_changed(self, row_idx, decision, row_num=None):
        """Gérer le changement de décision dans le tableau"""
        # Enregistrer la décision
        self.ext_df.loc[row_idx, 'decision_manuelle'] = decision
        
        # Si c'est une décision de conservation ou modification, ajouter aux whitelists
        if decision in ["Modifier", "Conserver"]:
            row = self.ext_df.loc[row_idx]
            anomalie = row.get('anomalie', '')
            if "Changement de profil à vérifier" in anomalie:
                ajouter_profil_valide(row, certificateur=self.parent_window.certificateur)
            if "Changement de direction à vérifier" in anomalie:
                ajouter_direction_conservee(row, certificateur=self.parent_window.certificateur)
        
        # Colorer la ligne si row_num est fourni
        if row_num is not None and self.manual_table.rowCount() > row_num:
            self.color_table_row(row_num, decision)
        
        # Mettre à jour les données
        self.update_after_decision_change()
        
        # Message de confirmation
        if decision:
            self.parent_window.show_status_message(f"✅ Décision '{decision}' enregistrée", 2000)
    
    def update_after_decision_change(self):
        """Mettre à jour après un changement de décision"""
        # Mettre à jour les cas à vérifier
        self.cas_a_verifier = extraire_cas_a_verifier(self.ext_df)
        
        # Mettre à jour les statistiques
        cas_automatiques = extraire_cas_automatiques(self.ext_df)
        comptes_valides = self.extraire_comptes_valides(self.ext_df)
        
        validated = len(comptes_valides)
        manual = len(self.cas_a_verifier)
        auto = len(cas_automatiques)
        
        self.stat_validated.set_value(str(validated))
        self.stat_manual.set_value(str(manual))
        self.stat_auto.set_value(str(auto))
        
        # Mettre à jour les badges
        self.anomalies_tabs.setTabText(0, f"🔍 Cas à vérifier manuellement ({manual})")
        self.anomalies_tabs.setTabText(2, f"✅ Comptes validés ({validated})")
        
        # Reconfigurer le bouton suivant
        self.configure_next_button(manual)
    
    def extraire_comptes_valides(self, ext_df):
        """Extraire les comptes sans anomalies (validés automatiquement)"""
        return ext_df[
            (ext_df['anomalie'].str.len() == 0) | 
            (ext_df['anomalie'].isna())
        ]
    
    def fill_validated_table(self, comptes_valides):
        """Remplir le tableau des comptes validés"""
        columns = ['code_utilisateur', 'nom_prenom', 'profil', 'direction']
        
        self.validated_table.setRowCount(len(comptes_valides))
        self.validated_table.setColumnCount(len(columns))
        self.validated_table.setHorizontalHeaderLabels(
            ['Code utilisateur', 'Nom/Prénom', 'Profil', 'Direction']
        )
        
        for i, (idx, row) in enumerate(comptes_valides.iterrows()):
            # Code utilisateur
            item = QTableWidgetItem(str(row['code_utilisateur']))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.validated_table.setItem(i, 0, item)
            
            # Nom/Prénom
            item = QTableWidgetItem(str(row['nom_prenom']))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.validated_table.setItem(i, 1, item)
            
            # Profil
            item = QTableWidgetItem(str(row.get('profil', 'N/A')))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.validated_table.setItem(i, 2, item)
            
            # Direction
            item = QTableWidgetItem(str(row.get('direction', 'N/A')))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.validated_table.setItem(i, 3, item)
            
            # Colorer toute la ligne en vert très sombre pour indiquer la validation
            color = QColor("#001a00")  # Vert très sombre
            for col in range(4):
                self.validated_table.item(i, col).setBackground(color)
        
        # Ajuster les colonnes
        self.adjust_table_columns(self.validated_table)
    
    def on_bulk_action(self, index):
        """Gérer les actions groupées sur les anomalies manuelles"""
        if index == 0:  # "Actions groupées..."
            return
        
        action = self.select_all_combo.currentText()
        
        if action == "Tout désactiver":
            decision = "Désactiver"
        elif action == "Tout conserver":
            decision = "Conserver"
        elif action == "Réinitialiser":
            decision = ""
        else:
            return
        
        # Confirmation
        if decision:
            # Compter uniquement les cas manuels
            manual_mask = (self.ext_df['anomalie'].str.len() > 0) & \
                         (~self.ext_df.get('cas_automatique', False))
            nb_manual = manual_mask.sum()
            
            reply = show_question_message(
                self,
                "Confirmation",
                f"Voulez-vous vraiment appliquer '{decision}' à tous les {nb_manual} cas manuels?"
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                self.select_all_combo.setCurrentIndex(0)
                return
        
        # Appliquer la décision uniquement aux cas manuels
        manual_mask = (self.ext_df['anomalie'].str.len() > 0) & \
                     (~self.ext_df.get('cas_automatique', False))
        self.ext_df.loc[manual_mask, 'decision_manuelle'] = decision
        
        # Si conservation, ajouter aux whitelists
        if decision == "Conserver":
            for idx, row in self.ext_df[manual_mask].iterrows():
                anomalie = row.get('anomalie', '')
                if "Changement de profil à vérifier" in anomalie:
                    ajouter_profil_valide(row, certificateur=self.parent_window.certificateur)
                if "Changement de direction à vérifier" in anomalie:
                    ajouter_direction_conservee(row, certificateur=self.parent_window.certificateur)
        
        # Mettre à jour l'affichage
        self.update_page(self.ext_df)
        self.parent_window.show_status_message(f"✅ Action '{action}' appliquée aux cas manuels", 3000)
        
        # Réinitialiser le combo
        self.select_all_combo.setCurrentIndex(0)