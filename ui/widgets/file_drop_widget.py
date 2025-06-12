"""
Widget qui accepte le glisser-déposer de fichiers compatible PyQt6
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect, QTimer
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from ui.styles import FILE_DROP_NORMAL_STYLE, FILE_DROP_HOVER_STYLE


class FileDropWidget(QWidget):
    """Widget qui accepte le glisser-déposer de fichiers avec effets visuels"""
    
    filesDropped = pyqtSignal(list)
    
    def __init__(self, label_text, accepted_extensions=None):
        super().__init__()
        self.accepted_extensions = accepted_extensions or ['.xlsx']
        self.label_text = label_text
        self.is_hovering = False
        self.setup_ui()
        
    def setup_ui(self):
        """Configurer l'interface du widget"""
        self.setAcceptDrops(True)
        
        layout = QVBoxLayout(self)
        self.label = QLabel(self.label_text)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet(FILE_DROP_NORMAL_STYLE)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)
        
        # Animation pour les transitions (simplifiée)
        self.animation = QPropertyAnimation(self.label, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Gérer l'entrée d'un élément glissé"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.is_hovering = True
            self.update_hover_state(True)
    
    def dragLeaveEvent(self, event):
        """Gérer la sortie d'un élément glissé"""
        self.is_hovering = False
        self.update_hover_state(False)
    
    def dropEvent(self, event: QDropEvent):
        """Gérer le dépôt de fichiers"""
        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if any(file_path.endswith(ext) for ext in self.accepted_extensions):
                files.append(file_path)
        
        if files:
            self.filesDropped.emit(files)
            # Effet de succès
            self.show_success_effect()
        
        self.is_hovering = False
        self.update_hover_state(False)
    
    def update_hover_state(self, is_hover):
        """Mettre à jour l'état de survol"""
        if is_hover:
            self.label.setStyleSheet(FILE_DROP_HOVER_STYLE)
        else:
            self.label.setStyleSheet(FILE_DROP_NORMAL_STYLE)
    
    def show_success_effect(self):
        """Afficher un effet de succès lors du dépôt"""
        success_style = """
        QLabel {
            border: 2px solid #81c784;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(129, 199, 132, 0.3),
                stop:1 rgba(129, 199, 132, 0.1));
            color: #81c784;
            border-radius: 12px;
            padding: 24px;
        }
        """
        
        self.label.setStyleSheet(success_style)
        
        # Retour au style normal après un délai
        QTimer.singleShot(1000, lambda: self.label.setStyleSheet(FILE_DROP_NORMAL_STYLE))
    
    def enterEvent(self, event):
        """Gérer l'entrée de la souris (effet hover subtil)"""
        if not self.is_hovering:
            subtle_hover_style = """
            QLabel {
                border: 2px dashed rgba(79, 195, 247, 0.5);
                border-radius: 12px;
                padding: 24px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.1),
                    stop:1 rgba(255, 255, 255, 0.05));
                color: rgba(255, 255, 255, 0.9);
            }
            """
            self.label.setStyleSheet(subtle_hover_style)
    
    def leaveEvent(self, event):
        """Gérer la sortie de la souris"""
        if not self.is_hovering:
            self.label.setStyleSheet(FILE_DROP_NORMAL_STYLE)