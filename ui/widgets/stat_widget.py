"""
Widget de statistiques réutilisable
"""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui.styles import STAT_WIDGET_STYLE, STAT_VALUE_STYLE, STAT_COLORS


class StatWidget(QFrame):
    """Widget d'affichage de statistiques avec valeur et label"""
    
    def __init__(self, label, value="0", color="#4fc3f7"):
        super().__init__()
        self.color = color
        self.setup_ui(label, value)
    
    def setup_ui(self, label, value):
        """Configurer l'interface du widget"""
        self.setFrameStyle(QFrame.Shape.Box)
        
        # Mapper les couleurs vers RGB pour le glassmorphism
        color_rgb = self.get_color_rgb(self.color)
        self.setStyleSheet(STAT_WIDGET_STYLE.format(color_rgb=color_rgb))
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Label de valeur avec effet glow
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet(STAT_VALUE_STYLE.format(color=self.color))
        layout.addWidget(self.value_label)
        
        # Label de texte avec style moderne
        text_label = QLabel(label)
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            font-size: 13px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        """)
        layout.addWidget(text_label)
    
    def get_color_rgb(self, hex_color):
        """Convertir couleur hex vers RGB pour les styles"""
        if hex_color == "#2196F3" or hex_color == "#1976d2":
            return STAT_COLORS["blue"]
        elif hex_color == "#4CAF50":
            return STAT_COLORS["green"]
        elif hex_color == "#FF9800":
            return STAT_COLORS["orange"]
        elif hex_color == "#F44336":
            return STAT_COLORS["red"]
        elif hex_color == "#9C27B0":
            return STAT_COLORS["purple"]
        else:
            # Par défaut, retourner bleu
            return STAT_COLORS["blue"]
    
    def set_value(self, value):
        """Mettre à jour la valeur affichée avec animation subtile"""
        self.value_label.setText(str(value))
        # Effet de flash subtil lors du changement
        self.value_label.setStyleSheet(f"""
            {STAT_VALUE_STYLE.format(color=self.color)}
            animation: pulse 0.3s ease-in-out;
        """)
    
    def get_value(self):
        """Récupérer la valeur actuelle"""
        return self.value_label.text()