"""
Fenêtre de connexion distincte
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QFrame, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor
from security.auth.auth_manager import auth_manager
from security.auth.user_store import user_store


class LoginWindow(QMainWindow):
    """Fenêtre de connexion distincte"""
    
    login_successful = pyqtSignal(str)  # Émet le nom d'utilisateur
    login_cancelled = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Certificateur de Comptes - Connexion")
        self.setFixedSize(1000, 800)  # Mêmes dimensions que la fenêtre principale
        
        # Variables d'état
        self.failed_attempts = 0
        self.max_attempts = 3
        
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
        """Configurer l'interface de la fenêtre"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Arrière-plan principal
        self.background_frame = QFrame()
        self.background_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0a0a, 
                    stop:0.3 #1a1a1a,
                    stop:0.7 #0d0d0d,
                    stop:1 #000000);
                border: none;
            }
        """)
        main_layout.addWidget(self.background_frame)
        
        # Layout de l'arrière-plan
        bg_layout = QVBoxLayout(self.background_frame)
        bg_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bg_layout.setContentsMargins(50, 50, 50, 50)
        
        # En-tête avec logo/titre
        self.create_header(bg_layout)
        
        # Conteneur de connexion centré
        self.create_login_container(bg_layout)
        
        # Pied de page
        self.create_footer(bg_layout)
    
    def create_header(self, parent_layout):
        """Créer l'en-tête de la fenêtre"""
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.setSpacing(10)
        
        # Logo/Titre principal
        title = QLabel("🔐 GATEKEEPER")
        title.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #800020;
                margin-bottom: 10px;
                background: transparent;
            }
        """)
        header_layout.addWidget(title)
        
        # Sous-titre
        subtitle = QLabel("Certificateur de Comptes")
        subtitle.setFont(QFont("Arial", 18, QFont.Weight.Normal))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                color: #cccccc;
                background: transparent;
                margin-bottom: 30px;
            }
        """)
        header_layout.addWidget(subtitle)
        
        parent_layout.addWidget(header_widget)
    
    def create_login_container(self, parent_layout):
        """Créer le conteneur de connexion avec taille ajustée"""
        # Conteneur principal centré - taille augmentée
        container_widget = QWidget()
        container_widget.setFixedSize(450, 420)  # Hauteur augmentée de 380 à 420
        container_layout = QVBoxLayout(container_widget)
        
        # Cadre de connexion
        self.login_frame = QFrame()
        self.login_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a, 
                    stop:0.3 #1a1a1a,
                    stop:0.7 #0d0d0d,
                    stop:1 #0a0a0a);
                border: 2px solid #800020;
                border-radius: 16px;
                padding: 25px;
            }
        """)
        container_layout.addWidget(self.login_frame)
        
        # Contenu du formulaire
        self.create_login_form()
        
        parent_layout.addWidget(container_widget, alignment=Qt.AlignmentFlag.AlignCenter)
    
    def create_login_form(self):
        """Créer le formulaire de connexion avec espacement amélioré"""
        layout = QVBoxLayout(self.login_frame)
        layout.setContentsMargins(40, 45, 40, 45)  # Marges augmentées
        
        # Champ nom d'utilisateur
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("👤 Nom d'utilisateur")
        self.username_input.setFixedHeight(50)
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(26, 26, 26, 0.9);
                border: 2px solid #333333;
                border-radius: 10px;
                padding: 0 20px;
                font-size: 15px;
                color: #ffffff;
                margin-bottom: 15px;
            }
            QLineEdit:focus {
                border: 2px solid #800020;
                background-color: rgba(26, 26, 26, 1.0);
            }
            QLineEdit::placeholder {
                color: #888888;
            }
        """)
        layout.addWidget(self.username_input)
        
        # Espacement supplémentaire entre les champs
        layout.addSpacing(15)
        
        # Champ mot de passe
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("🔑 Mot de passe")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(50)
        self.password_input.setStyleSheet(self.username_input.styleSheet())
        layout.addWidget(self.password_input)
        
        # Espacement avant le message d'erreur
        layout.addSpacing(20)
        
        # Message d'erreur
        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setFixedHeight(30)  # Hauteur augmentée
        self.error_label.setStyleSheet("""
            QLabel {
                color: #ff5555;
                font-size: 13px;
                font-weight: bold;
                background: transparent;
            }
        """)
        layout.addWidget(self.error_label)
        
        # Espacement avant les boutons
        layout.addSpacing(25)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(25)  # Espacement entre boutons augmenté
        
        # Bouton Quitter
        self.quit_button = QPushButton("Quitter")
        self.quit_button.setFixedHeight(45)
        self.quit_button.setFixedWidth(120)
        self.quit_button.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                border: 1px solid #555555;
                border-radius: 8px;
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
        buttons_layout.addWidget(self.quit_button)
        
        # Bouton Connexion
        self.login_button = QPushButton("Se connecter")
        self.login_button.setFixedHeight(45)
        self.login_button.setFixedWidth(150)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #800020;
                border: none;
                border-radius: 8px;
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
        buttons_layout.addWidget(self.login_button)
        
        layout.addLayout(buttons_layout)
        
        # Événements clavier
        self.username_input.returnPressed.connect(self.password_input.setFocus)
        self.password_input.returnPressed.connect(self.on_login)
    
    def create_footer(self, parent_layout):
        """Créer le pied de page"""
        footer_widget = QWidget()
        footer_layout = QVBoxLayout(footer_widget)
        footer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_layout.setSpacing(5)
        
        # Informations par défaut
        default_info = QLabel("💡 Utilisateur par défaut: admin | Mot de passe: admin123")
        default_info.setFont(QFont("Arial", 12))
        default_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        default_info.setStyleSheet("""
            QLabel {
                color: #666666;
                background: transparent;
                margin-top: 20px;
            }
        """)
        footer_layout.addWidget(default_info)
        
        # Version
        version_label = QLabel("Gatekeeper v2.0 - Certificateur de Comptes")
        version_label.setFont(QFont("Arial", 10))
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("""
            QLabel {
                color: #555555;
                background: transparent;
                margin-top: 5px;
            }
        """)
        footer_layout.addWidget(version_label)
        
        parent_layout.addWidget(footer_widget)
    
    def center_window(self):
        """Centrer la fenêtre sur l'écran"""
        screen = QApplication.primaryScreen().geometry()
        window_geometry = self.geometry()
        x = (screen.width() - window_geometry.width()) // 2
        y = (screen.height() - window_geometry.height()) // 2
        self.move(x, y)
    
    def showEvent(self, event):
        """Événement d'affichage"""
        super().showEvent(event)
        # Focus sur le premier champ
        QTimer.singleShot(100, self.username_input.setFocus)
    
    def on_login(self):
        """Gérer la tentative de connexion"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Validation des champs
        if not username or not password:
            self.show_error("Veuillez renseigner tous les champs")
            return
        
        # Vérifier si le compte est verrouillé
        if auth_manager.is_account_locked(username):
            self.show_error("Compte temporairement verrouillé (15 min)")
            return
        
        # Désactiver le bouton pendant la vérification
        self.login_button.setEnabled(False)
        self.login_button.setText("Vérification...")
        
        # Délai pour simulation du traitement
        QTimer.singleShot(500, lambda: self.process_login(username, password))
    
    def process_login(self, username, password):
        """Traiter la connexion après délai"""
        # Tentative d'authentification
        if auth_manager.authenticate(username, password, user_store):
            self.clear_error()
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
            
            # Réactiver le bouton
            self.login_button.setEnabled(True)
            self.login_button.setText("Se connecter")
            
            # Vider le mot de passe
            self.password_input.clear()
            self.password_input.setFocus()
    
    def on_quit(self):
        """Gérer la fermeture"""
        self.login_cancelled.emit()
        self.close()
    
    def force_quit(self):
        """Forcer la fermeture après trop de tentatives"""
        self.login_cancelled.emit()
        QApplication.quit()
    
    def show_error(self, message):
        """Afficher un message d'erreur"""
        self.error_label.setText(message)
        
        # Style d'erreur pour les champs
        error_style = """
            QLineEdit {
                background-color: rgba(60, 20, 20, 0.9);
                border: 2px solid #ff5555;
                border-radius: 10px;
                padding: 0 20px;
                font-size: 15px;
                color: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #ff3333;
                background-color: rgba(60, 20, 20, 1.0);
            }
            QLineEdit::placeholder {
                color: #888888;
            }
        """
        self.username_input.setStyleSheet(error_style)
        self.password_input.setStyleSheet(error_style)
        
        # Animation de secousse (optionnelle)
        self.shake_animation()
    
    def shake_animation(self):
        """Animation de secousse pour le formulaire"""
        self.animation = QPropertyAnimation(self.login_frame, b"geometry")
        self.animation.setDuration(500)
        self.animation.setEasingCurve(QEasingCurve.Type.OutBounce)
        
        original_geometry = self.login_frame.geometry()
        shaken_geometry = QRect(
            original_geometry.x() + 10,
            original_geometry.y(),
            original_geometry.width(),
            original_geometry.height()
        )
        
        self.animation.setStartValue(shaken_geometry)
        self.animation.setEndValue(original_geometry)
        self.animation.start()
    
    def clear_error(self):
        """Effacer le message d'erreur"""
        self.error_label.setText("")
        
        # Restaurer le style normal
        normal_style = """
            QLineEdit {
                background-color: rgba(26, 26, 26, 0.9);
                border: 2px solid #333333;
                border-radius: 10px;
                padding: 0 20px;
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
        """
        self.username_input.setStyleSheet(normal_style)
        self.password_input.setStyleSheet(normal_style)
    
    def keyPressEvent(self, event):
        """Gérer les événements clavier"""
        if event.key() == Qt.Key.Key_Escape:
            self.on_quit()
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Gérer la fermeture de la fenêtre"""
        # Émettre le signal d'annulation si pas de connexion réussie
        if not auth_manager.is_authenticated():
            self.login_cancelled.emit()
        super().closeEvent(event)
