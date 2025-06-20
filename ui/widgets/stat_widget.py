"""
Widget de statistiques réutilisable compatible PyQt6
Thème rouge bordeaux, noir et blanc
"""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui.styles import STAT_VALUE_STYLE, STAT_COLORS


class StatWidget(QFrame):
    """Widget d'affichage de statistiques avec valeur et label - Thème rouge bordeaux"""
    
    def __init__(self, label, value="0", color="#B22222"):
        super().__init__()
        self.color = color
        self.setup_ui(label, value)
    
    def setup_ui(self, label, value):
        """Configurer l'interface du widget avec thème rouge bordeaux"""
        self.setFrameStyle(QFrame.Shape.Box)
        
        # Mapper les couleurs vers hex - adaptation thème rouge
        color_hex = self.get_color_hex(self.color)
        widget_style = f"""
        QFrame {{
            background-color: #0a0a0a;
            border: 2px solid #{color_hex};
            border-radius: 8px;
            padding: 20px;
            min-width: 160px;
        }}
        """
        self.setStyleSheet(widget_style)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Label de valeur
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet(STAT_VALUE_STYLE.format(color=self.color))
        layout.addWidget(self.value_label)
        
        # Label de texte
        text_label = QLabel(label)
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            font-size: 13px;
            font-weight: 600;
        """)
        layout.addWidget(text_label)
    
    def get_color_hex(self, hex_color):
        """Mapper couleur hex vers hex sans # - adaptation thème rouge bordeaux"""
        # Nouvelles couleurs pour le thème rouge bordeaux
        if hex_color == "#2196F3" or hex_color == "#1976d2" or hex_color == "#0066cc":
            return "800020"  # Rouge bordeaux principal
        elif hex_color == "#4CAF50":
            return STAT_COLORS["green"]  # Vert conservé
        elif hex_color == "#FF9800":
            return STAT_COLORS["orange"]  # Orange conservé
        elif hex_color == "#F44336":
            return "ff3333"  # Rouge vif pour erreurs
        elif hex_color == "#9C27B0":
            return STAT_COLORS["purple"]  # Violet conservé
        elif hex_color == "#B22222":
            return "B22222"  # Rouge accent
        elif hex_color == "#A52A2A":
            return "A52A2A"  # Rouge bordeaux clair
        elif hex_color == "#800020":
            return "800020"  # Rouge bordeaux principal
        else:
            # Par défaut, retourner rouge bordeaux
            return "800020"
    
    def set_value(self, value):
        """Mettre à jour la valeur affichée"""
        self.value_label.setText(str(value))
    
    def get_value(self):
        """Récupérer la valeur actuelle"""
        return self.value_label.text()