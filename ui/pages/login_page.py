"""
Fenêtre de connexion réimplémentée sans margins/spacing, uniquement avec padding
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QFrame, QApplication, QCheckBox,
                            QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect, QTimer, QPoint
from PyQt6.QtGui import QFont, QPalette, QColor
from security.auth.auth_manager import auth_manager
from security.auth.user_store import user_store
from resource_path import persistent_data_path
import os
import json
from datetime import datetime


class LoginWindow(QMainWindow):
    """Fenêtre de connexion réimplémentée avec padding uniquement"""
    
    login_successful = pyqtSignal(str)
    login_cancelled = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Certificateur de Comptes - Connexion")
        self.setFixedSize(1000, 800)
        
        # Variables d'état
        self.failed_attempts = 0
        self.max_attempts = 3
        self.password_visible = False
        self.loading_index = 0
        
        self.setup_window_style()
        self.setup_ui()
        self.center_window()
    
    def setup_window_style(self):
        """Configurer le style de la fenêtre"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
                color: #ffffff;
            }
        """)
    
    def setup_ui(self):
        """Configurer l'interface - tout en padding"""
        # Widget central avec padding global
        central_widget = QWidget()
        central_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0a0a, 
                    stop:0.3 #1a1a1a,
                    stop:0.7 #0d0d0d,
                    stop:1 #000000);
                padding: 50px;
            }
        """)
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Container principal avec padding interne
        main_container = QWidget()
        main_container.setMaximumWidth(500)
        main_container.setStyleSheet("""
            QWidget {
                background: transparent;
                padding: 0px;
            }
        """)
        
        container_layout = QVBoxLayout(main_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Header
        self.create_header_section(container_layout)
        container_layout.addSpacing(20)
        
        # Formulaire de connexion
        self.create_login_form_section(container_layout)
        container_layout.addSpacing(20)
        
        # Footer
        self.create_footer_section(container_layout)
        
        main_layout.addWidget(main_container)
    
    def create_header_section(self, parent_layout):
        """Créer l'en-tête avec padding"""
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background: transparent;
                padding: 0px 0px 40px 0px;
            }
        """)
        
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)
        
        # Logo/Titre
        title_label = QLabel("🔐 GATEKEEPER")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #800020;
                font-size: 36px;
                font-weight: bold;
                padding: 0px 0px 10px 0px;
                background: transparent;
            }
        """)
        header_layout.addWidget(title_label)
        
        # Sous-titre
        subtitle_label = QLabel("Certificateur de Comptes")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 18px;
                padding: 0px;
                background: transparent;
            }
        """)
        header_layout.addWidget(subtitle_label)
        
        parent_layout.addWidget(header_widget)
    
    def create_login_form_section(self, parent_layout):
        """Créer le formulaire de connexion"""
        # Container du formulaire avec style glass
        self.form_container = QFrame()
        self.form_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(42, 42, 42, 0.95), 
                    stop:0.3 rgba(26, 26, 26, 0.9),
                    stop:0.7 rgba(13, 13, 13, 0.85),
                    stop:1 rgba(10, 10, 10, 0.8));
                border: 2px solid #800020;
                border-radius: 16px;
                padding: 45px 40px;
            }
        """)
        
        form_layout = QVBoxLayout(self.form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(0)
        
        # Champ utilisateur
        self.create_username_field(form_layout)
        form_layout.addSpacing(15)
        
        # Champ mot de passe
        self.create_password_field(form_layout)
        form_layout.addSpacing(8)
        
        # Indicateur Caps Lock
        self.create_caps_lock_indicator(form_layout)
        form_layout.addSpacing(10)
        
        # Checkbox Se souvenir
        self.create_remember_checkbox(form_layout)
        form_layout.addSpacing(15)
        
        # Message d'erreur
        self.create_error_label(form_layout)
        form_layout.addSpacing(10)
        
        # Boutons
        self.create_buttons(form_layout)
        
        parent_layout.addWidget(self.form_container)
    
    def create_username_field(self, parent_layout):
        """Créer le champ nom d'utilisateur"""
        username_container = QWidget()
        username_container.setStyleSheet("""
            QWidget {
                background: transparent;
                padding: 0px;
            }
        """)
        
        username_layout = QVBoxLayout(username_container)
        username_layout.setContentsMargins(0, 0, 0, 0)
        username_layout.setSpacing(0)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("👤 Nom d'utilisateur")
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(26, 26, 26, 0.9);
                border: 2px solid #333333;
                border-radius: 10px;
                padding: 15px 20px;
                font-size: 15px;
                color: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #800020;
                background-color: rgba(26, 26, 26, 1.0);
            }
            QLineEdit::placeholder {
                color: #888888;
            }
        """)
        username_layout.addWidget(self.username_input)
        
        parent_layout.addWidget(username_container)
    
    def create_password_field(self, parent_layout):
        """Créer le champ mot de passe avec toggle"""
        password_container = QWidget()
        password_container.setStyleSheet("""
            QWidget {
                background: transparent;
                padding: 0px;
            }
        """)
        
        password_layout = QVBoxLayout(password_container)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(0)
        
        # Container pour le champ et le bouton
        field_container = QWidget()
        field_layout = QHBoxLayout(field_container)
        field_layout.setContentsMargins(0, 0, 0, 0)
        field_layout.setSpacing(0)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("🔑 Mot de passe")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(26, 26, 26, 0.9);
                border: 2px solid #333333;
                border-radius: 10px;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
                padding: 15px 20px;
                font-size: 15px;
                color: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #800020;
                background-color: rgba(26, 26, 26, 1.0);
            }
            QLineEdit::placeholder {
                color: #888888;
            }
        """)
        field_layout.addWidget(self.password_input)
        
        # Bouton toggle
        self.password_toggle = QPushButton("👁")
        self.password_toggle.setFixedWidth(50)
        self.password_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.password_toggle.setStyleSheet("""
            QPushButton {
                background-color: rgba(26, 26, 26, 0.9);
                border: 2px solid #333333;
                border-left: none;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
                padding: 15px 0px;
                color: #999999;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(40, 40, 40, 0.9);
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: rgba(20, 20, 20, 0.9);
                color: #800020;
            }
        """)
        self.password_toggle.clicked.connect(self.toggle_password_visibility)
        field_layout.addWidget(self.password_toggle)
        
        password_layout.addWidget(field_container)
        parent_layout.addWidget(password_container)
    
    def create_caps_lock_indicator(self, parent_layout):
        """Créer l'indicateur Caps Lock"""
        self.caps_lock_warning = QLabel("⚠️ Caps Lock activé")
        self.caps_lock_warning.setStyleSheet("""
            QLabel {
                color: #ffaa00;
                font-size: 12px;
                font-weight: bold;
                background: transparent;
                padding: 5px 0px 10px 0px;
            }
        """)
        self.caps_lock_warning.setVisible(False)
        parent_layout.addWidget(self.caps_lock_warning)
    
    def create_remember_checkbox(self, parent_layout):
        """Créer la checkbox Se souvenir"""
        checkbox_container = QWidget()
        checkbox_container.setStyleSheet("""
            QWidget {
                background: transparent;
                padding: 0px;
            }
        """)
        
        checkbox_layout = QVBoxLayout(checkbox_container)
        checkbox_layout.setContentsMargins(0, 0, 0, 0)
        checkbox_layout.setSpacing(0)
        
        self.remember_checkbox = QCheckBox("Se souvenir de moi")
        self.remember_checkbox.setStyleSheet("""
            QCheckBox {
                color: #cccccc;
                font-size: 13px;
                padding: 0px;
                background: transparent;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #333333;
                background-color: rgba(26, 26, 26, 0.9);
            }
            QCheckBox::indicator:checked {
                background-color: #800020;
                border: 2px solid #800020;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #A52A2A;
            }
        """)
        checkbox_layout.addWidget(self.remember_checkbox)
        
        parent_layout.addWidget(checkbox_container)
    
    def create_error_label(self, parent_layout):
        """Créer le label d'erreur"""
        error_container = QWidget()
        error_container.setStyleSheet("""
            QWidget {
                background: transparent;
                padding: 0px;
            }
        """)
        
        error_layout = QVBoxLayout(error_container)
        error_layout.setContentsMargins(0, 0, 0, 0)
        error_layout.setSpacing(0)
        
        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setStyleSheet("""
            QLabel {
                color: #ff5555;
                font-size: 13px;
                font-weight: bold;
                background: rgba(60, 20, 20, 0.5);
                border-radius: 6px;
                padding: 8px;
            }
        """)
        self.error_label.setVisible(False)
        error_layout.addWidget(self.error_label)
        
        parent_layout.addWidget(error_container)
    
    def create_buttons(self, parent_layout):
        """Créer les boutons"""
        buttons_container = QWidget()
        buttons_container.setStyleSheet("""
            QWidget {
                background: transparent;
                padding: 0px;
            }
        """)
        
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(0)
        
        # Bouton Quitter
        quit_container = QWidget()
        quit_container.setStyleSheet("padding: 0px 12px 0px 0px; background: transparent;")
        quit_layout = QVBoxLayout(quit_container)
        quit_layout.setContentsMargins(0, 0, 0, 0)
        
        self.quit_button = QPushButton("Quitter")
        self.quit_button.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                border: 1px solid #555555;
                border-radius: 8px;
                padding: 12px 30px;
                color: #ffffff;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #444444;
                border: 1px solid #666666;
            }
            QPushButton:pressed {
                background-color: #222222;
            }
        """)
        self.quit_button.clicked.connect(self.on_quit)
        quit_layout.addWidget(self.quit_button)
        
        buttons_layout.addWidget(quit_container)
        
        # Spacer
        spacer = QWidget()
        spacer.setStyleSheet("background: transparent;")
        buttons_layout.addWidget(spacer, 1)
        
        # Bouton Connexion
        login_container = QWidget()
        login_container.setStyleSheet("padding: 0px 0px 0px 12px; background: transparent;")
        login_layout = QVBoxLayout(login_container)
        login_layout.setContentsMargins(0, 0, 0, 0)
        
        self.login_button = QPushButton("Se connecter")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #800020;
                border: none;
                border-radius: 8px;
                padding: 12px 40px;
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #A52A2A;
            }
            QPushButton:pressed {
                background-color: #600018;
            }
            QPushButton:disabled {
                background-color: #333333;
                color: #666666;
            }
        """)
        self.login_button.clicked.connect(self.on_login)
        self.login_button.setDefault(True)
        login_layout.addWidget(self.login_button)
        
        buttons_layout.addWidget(login_container)
        
        parent_layout.addWidget(buttons_container)
    
    def create_footer_section(self, parent_layout):
        """Créer le pied de page"""
        footer_widget = QWidget()
        footer_widget.setStyleSheet("""
            QWidget {
                background: transparent;
                padding: 40px 0px 0px 0px;
            }
        """)
        
        footer_layout = QVBoxLayout(footer_widget)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(0)
        
        # Version seulement (suppression du label info)
        version_label = QLabel("Gatekeeper v2.0 - Certificateur de Comptes")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("""
            QLabel {
                color: #555555;
                font-size: 10px;
                padding: 0px;
                background: transparent;
            }
        """)
        footer_layout.addWidget(version_label)
        
        parent_layout.addWidget(footer_widget)
    
    # === Méthodes fonctionnelles ===
    
    def center_window(self):
        """Centrer la fenêtre sur l'écran"""
        screen = QApplication.primaryScreen().geometry()
        window_geometry = self.geometry()
        x = (screen.width() - window_geometry.width()) // 2
        y = (screen.height() - window_geometry.height()) // 2
        self.move(x, y)
    
    def toggle_password_visibility(self):
        """Basculer la visibilité du mot de passe"""
        if self.password_visible:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.password_toggle.setText("👁")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.password_toggle.setText("👁‍🗨")
        self.password_visible = not self.password_visible
    
    def showEvent(self, event):
        """Événement d'affichage"""
        super().showEvent(event)
        self.load_remember_preference()
        
        # Connecter les événements
        self.username_input.returnPressed.connect(self.password_input.setFocus)
        self.password_input.returnPressed.connect(self.on_login)
        self.password_input.textChanged.connect(self.check_caps_lock_state)
        
        # Focus initial
        if not self.username_input.text():
            QTimer.singleShot(100, self.username_input.setFocus)
        else:
            QTimer.singleShot(100, self.password_input.setFocus)
    
    def check_caps_lock_state(self):
        """Vérifier l'état du Caps Lock"""
        modifiers = QApplication.keyboardModifiers()
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            self.caps_lock_warning.setVisible(True)
        else:
            self.caps_lock_warning.setVisible(False)
    
    def on_login(self):
        """Gérer la tentative de connexion"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Effacer l'erreur précédente
        self.clear_error()
        
        # Validation
        if not username:
            self.show_field_error(self.username_input, "Nom d'utilisateur requis")
            return
        if not password:
            self.show_field_error(self.password_input, "Mot de passe requis")
            return
        
        # Vérifier le verrouillage
        if auth_manager.is_account_locked(username):
            self.show_error("Compte verrouillé. Réessayez dans 15 minutes.")
            return
        
        # Animation de chargement
        self.login_button.setEnabled(False)
        self.create_loading_animation()
        
        # Traitement
        QTimer.singleShot(500, lambda: self.process_login(username, password))
    
    def process_login(self, username, password):
        """Traiter la connexion"""
        self.stop_loading_animation()
        
        if auth_manager.authenticate(username, password, user_store):
            self.clear_error()
            self.save_remember_preference(username)
            self.login_successful.emit(username)
            self.close()
        else:
            self.failed_attempts += 1
            remaining = self.max_attempts - self.failed_attempts
            
            if remaining > 0:
                self.show_error(f"Identifiants incorrects ({remaining} tentative(s) restante(s))")
            else:
                self.show_error("Trop de tentatives échouées. Application fermée.")
                QTimer.singleShot(2000, self.force_quit)
                return
            
            self.login_button.setEnabled(True)
            self.password_input.clear()
            self.password_input.setFocus()
    
    def show_error(self, message):
        """Afficher un message d'erreur"""
        self.error_label.setText(message)
        self.error_label.setVisible(True)
        
        # Animation fade in CORRIGÉE
        effect = QGraphicsOpacityEffect()
        self.error_label.setGraphicsEffect(effect)
        self.fade_animation = QPropertyAnimation(effect, b"opacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.start()
    
    def clear_error(self):
        """Effacer le message d'erreur"""
        self.error_label.setText("")
        self.error_label.setVisible(False)
    
    def show_field_error(self, field, message):
        """Afficher une erreur sur un champ spécifique"""
        self.show_error(message)
        
        # Animation de secousse
        self.shake_field(field)
        
        # Bordure rouge temporaire
        original_style = field.styleSheet()
        field.setStyleSheet(original_style.replace("#333333", "#ff3333"))
        QTimer.singleShot(2000, lambda: field.setStyleSheet(original_style))
    
    def shake_field(self, field):
        """Animation de secousse pour un champ"""
        original_pos = field.pos()
        
        animation = QPropertyAnimation(field, b"pos")
        animation.setDuration(500)
        animation.setKeyValueAt(0, original_pos)
        animation.setKeyValueAt(0.1, original_pos + QPoint(10, 0))
        animation.setKeyValueAt(0.2, original_pos + QPoint(-10, 0))
        animation.setKeyValueAt(0.3, original_pos + QPoint(10, 0))
        animation.setKeyValueAt(0.4, original_pos + QPoint(-10, 0))
        animation.setKeyValueAt(0.5, original_pos)
        animation.setEasingCurve(QEasingCurve.Type.OutElastic)
        animation.start()
    
    def create_loading_animation(self):
        """Créer l'animation de chargement"""
        loading_text = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        self.loading_index = 0
        
        def update_loading():
            if hasattr(self, 'loading_timer') and self.loading_timer.isActive():
                self.login_button.setText(f"Connexion {loading_text[self.loading_index % len(loading_text)]}")
                self.loading_index += 1
        
        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(update_loading)
        self.loading_timer.start(100)
    
    def stop_loading_animation(self):
        """Arrêter l'animation de chargement"""
        if hasattr(self, 'loading_timer'):
            self.loading_timer.stop()
        self.login_button.setText("Se connecter")
    
    def save_remember_preference(self, username):
        """Sauvegarder la préférence"""
        if self.remember_checkbox.isChecked():
            settings_file = persistent_data_path("login_preferences.json")
            preferences = {
                "remember": True,
                "username": username,
                "timestamp": datetime.now().isoformat()
            }
            with open(settings_file, 'w') as f:
                json.dump(preferences, f)
    
    def load_remember_preference(self):
        """Charger la préférence"""
        settings_file = persistent_data_path("login_preferences.json")
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    preferences = json.load(f)
                if preferences.get("remember"):
                    self.username_input.setText(preferences.get("username", ""))
                    self.remember_checkbox.setChecked(True)
                    return True
            except:
                pass
        return False
    
    def on_quit(self):
        """Gérer la fermeture"""
        self.login_cancelled.emit()
        self.close()
    
    def force_quit(self):
        """Forcer la fermeture"""
        self.login_cancelled.emit()
        QApplication.quit()
    
    def keyPressEvent(self, event):
        """Gérer les événements clavier"""
        if event.key() == Qt.Key.Key_Escape:
            self.on_quit()
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Gérer la fermeture de la fenêtre"""
        if not auth_manager.is_authenticated():
            self.login_cancelled.emit()
        super().closeEvent(event)
