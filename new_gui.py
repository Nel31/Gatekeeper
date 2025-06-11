#!/usr/bin/env python3
"""
Point d'entrée principal pour l'application GUI du Certificateur de Comptes
avec thème sombre moderne
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor
from ui.main_window import CertificateurApp


def setup_dark_palette(app):
    """Configurer la palette sombre pour l'application"""
    palette = QPalette()
    
    # Couleurs principales
    palette.setColor(QPalette.ColorRole.Window, QColor(15, 15, 15))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(26, 26, 26))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(31, 31, 31))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(35, 35, 35))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.ColorRole.Link, QColor(79, 195, 247))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(79, 195, 247))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
    
    app.setPalette(palette)


def main():
    """Point d'entrée principal de l'application"""
    app = QApplication(sys.argv)
    
    # Style moderne avec thème sombre
    app.setStyle('Fusion')
    
    # Appliquer la palette sombre
    setup_dark_palette(app)
    
    # Configuration de l'application
    app.setApplicationName("Certificateur de Comptes - Gatekeeper")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Gatekeeper")
    app.setOrganizationDomain("gatekeeper.local")
    
    # Définir l'icône de l'application (si disponible)
    # app.setWindowIcon(QIcon('resources/icon.png'))
    
    # Créer et afficher la fenêtre principale
    window = CertificateurApp()
    window.show()
    
    # Centrer la fenêtre sur l'écran
    try:
        screen = app.primaryScreen().geometry()
        window_geometry = window.geometry()
        x = (screen.width() - window_geometry.width()) // 2
        y = (screen.height() - window_geometry.height()) // 2
        window.move(x, y)
    except Exception as e:
        print(f"Impossible de centrer la fenêtre: {e}")
    
    # Message de bienvenue dans la console
    print("🌙 Certificateur de Comptes - Thème Sombre Activé")
    print("✨ Interface moderne avec glassmorphism")
    print("🚀 Application prête !")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()