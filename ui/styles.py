"""
Styles CSS compatibles avec PyQt6 - Thème très sombre sans glassmorphism
"""

MAIN_STYLE = """
QMainWindow {
    background-color: #000000;
    color: #ffffff;
}

QWidget {
    background-color: transparent;
    color: #ffffff;
}

QPushButton {
    background-color: #0d0d0d;
    border: 1px solid #1a1a1a;
    border-radius: 6px;
    padding: 12px 24px;
    font-weight: 600;
    font-size: 13px;
    color: #ffffff;
}

QPushButton:hover {
    background-color: #1a1a1a;
    border: 1px solid #333333;
}

QPushButton:pressed {
    background-color: #0a0a0a;
    border: 1px solid #1a1a1a;
}

QPushButton#primaryButton {
    background-color: #0066cc;
    border: 1px solid #0066cc;
    color: #ffffff;
    font-size: 14px;
    font-weight: 700;
}

QPushButton#primaryButton:hover {
    background-color: #0080ff;
    border: 1px solid #0080ff;
}

QPushButton#primaryButton:disabled {
    background-color: #1a1a1a;
    border: 1px solid #1a1a1a;
    color: #666666;
}

QPushButton#successButton {
    background-color: #00cc44;
    border: 1px solid #00cc44;
    color: #ffffff;
}

QPushButton#successButton:hover {
    background-color: #00ff55;
    border: 1px solid #00ff55;
}

QGroupBox {
    background-color: #0a0a0a;
    border: 1px solid #1a1a1a;
    border-radius: 8px;
    margin-top: 20px;
    padding-top: 20px;
    font-weight: 700;
    font-size: 14px;
    color: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 20px;
    padding: 8px 16px;
    background-color: #0066cc;
    border-radius: 6px;
    color: #ffffff;
    font-weight: 700;
}

QLineEdit {
    background-color: #0d0d0d;
    border: 1px solid #1a1a1a;
    border-radius: 6px;
    padding: 12px 16px;
    font-size: 13px;
    color: #ffffff;
}

QLineEdit:focus {
    border: 2px solid #0066cc;
    background-color: #1a1a1a;
}

QProgressBar {
    background-color: #0d0d0d;
    border: 1px solid #1a1a1a;
    border-radius: 6px;
    text-align: center;
    height: 24px;
    color: #ffffff;
    font-weight: 600;
}

QProgressBar::chunk {
    background-color: #0066cc;
    border-radius: 5px;
}

QTableWidget {
    background-color: #0d0d0d;
    border: 1px solid #1a1a1a;
    border-radius: 6px;
    gridline-color: #1a1a1a;
    color: #ffffff;
    alternate-background-color: #0a0a0a;
}

QTableWidget::item {
    padding: 8px;
    border: none;
}

QTableWidget::item:selected {
    background-color: #003366;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #0a0a0a;
    border: none;
    border-right: 1px solid #1a1a1a;
    padding: 12px 8px;
    font-weight: 700;
    color: #ffffff;
}

QTabWidget::pane {
    background-color: #0d0d0d;
    border: 1px solid #1a1a1a;
    border-radius: 6px;
    margin-top: 10px;
}

QTabWidget::tab-bar {
    alignment: center;
}

QTabBar::tab {
    background-color: #0a0a0a;
    border: 1px solid #1a1a1a;
    border-bottom: none;
    border-radius: 6px 6px 0 0;
    padding: 12px 20px;
    margin-right: 2px;
    color: #999999;
    font-weight: 600;
}

QTabBar::tab:selected {
    background-color: #0066cc;
    color: #ffffff;
    border: 1px solid #0066cc;
}

QTabBar::tab:hover:!selected {
    background-color: #1a1a1a;
    color: #ffffff;
}

QListWidget {
    background-color: #0d0d0d;
    border: 1px solid #1a1a1a;
    border-radius: 6px;
    color: #ffffff;
}

QListWidget::item {
    padding: 8px;
    border-bottom: 1px solid #1a1a1a;
}

QListWidget::item:selected {
    background-color: #003366;
}

QTextEdit {
    background-color: #0d0d0d;
    border: 1px solid #1a1a1a;
    border-radius: 6px;
    padding: 12px;
    color: #ffffff;
}

QTextEdit:focus {
    border: 2px solid #0066cc;
}

QScrollBar:vertical {
    background-color: #0a0a0a;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #333333;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #666666;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #0a0a0a;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #333333;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #666666;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QMenuBar {
    background-color: #0a0a0a;
    border-bottom: 1px solid #1a1a1a;
    color: #ffffff;
    padding: 4px;
}

QMenuBar::item {
    background: transparent;
    padding: 8px 16px;
    border-radius: 4px;
    margin: 2px;
}

QMenuBar::item:selected {
    background-color: #1a1a1a;
    color: #ffffff;
}

QMenu {
    background-color: #0d0d0d;
    border: 1px solid #1a1a1a;
    border-radius: 6px;
    color: #ffffff;
    padding: 8px;
}

QMenu::item {
    padding: 10px 20px;
    border-radius: 4px;
    margin: 2px;
}

QMenu::item:selected {
    background-color: #003366;
    color: #ffffff;
}

QStatusBar {
    background-color: #0a0a0a;
    border-top: 1px solid #1a1a1a;
    color: #ffffff;
    padding: 8px;
}

QComboBox {
    background-color: #0d0d0d;
    border: 1px solid #1a1a1a;
    border-radius: 6px;
    padding: 10px 16px;
    color: #ffffff;
}

QComboBox:hover {
    border: 1px solid #333333;
    background-color: #1a1a1a;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #ffffff;
    margin-right: 10px;
}

QComboBox QAbstractItemView {
    background-color: #0d0d0d;
    border: 1px solid #1a1a1a;
    border-radius: 6px;
    color: #ffffff;
    selection-background-color: #003366;
}

QRadioButton {
    color: #ffffff;
    spacing: 10px;
}

QRadioButton::indicator {
    width: 20px;
    height: 20px;
    border-radius: 10px;
}

QRadioButton::indicator:unchecked {
    border: 2px solid #333333;
    background-color: #0d0d0d;
}

QRadioButton::indicator:checked {
    border: 2px solid #0066cc;
    background-color: #0066cc;
}

QRadioButton::indicator:hover {
    border: 2px solid #0080ff;
    background-color: #1a1a1a;
}
"""

STEP_ACTIVE_STYLE = """
QLabel {
    border-radius: 15px;
    background-color: #0066cc;
    color: #ffffff;
    font-weight: 700;
    font-size: 14px;
    border: 1px solid #0066cc;
}
"""

STEP_COMPLETED_STYLE = """
QLabel {
    border-radius: 15px;
    background-color: #00cc44;
    color: #ffffff;
    font-weight: 700;
    font-size: 14px;
    border: 1px solid #00cc44;
}
"""

STEP_INACTIVE_STYLE = """
QLabel {
    border-radius: 15px;
    background-color: #0d0d0d;
    border: 1px solid #1a1a1a;
    color: #666666;
    font-weight: 600;
    font-size: 14px;
}
"""

STEP_TEXT_ACTIVE_STYLE = """
QLabel {
    color: #0080ff;
    font-weight: 700;
    font-size: 13px;
}
"""

STEP_TEXT_COMPLETED_STYLE = """
QLabel {
    color: #00ff55;
    font-weight: 600;
    font-size: 13px;
}
"""

STEP_TEXT_INACTIVE_STYLE = """
QLabel {
    color: #666666;
    font-weight: 500;
    font-size: 13px;
}
"""

VALID_ICON_STYLE = """
color: #00ff55; 
font-weight: bold; 
font-size: 16px;
"""

RADIO_BUTTON_STYLE = """
QRadioButton {
    padding: 12px;
    font-size: 13px;
    color: #ffffff;
    spacing: 10px;
}
QRadioButton::indicator {
    width: 20px;
    height: 20px;
    border-radius: 10px;
}
QRadioButton::indicator:unchecked {
    border: 2px solid #333333;
    background-color: #0d0d0d;
}
QRadioButton::indicator:checked {
    background-color: #0066cc;
    border: 2px solid #0066cc;
}
QRadioButton::indicator:hover {
    border: 2px solid #0080ff;
    background-color: #1a1a1a;
}
"""

COMBO_BOX_STYLE = """
QComboBox {
    background-color: #0d0d0d;
    border: 1px solid #1a1a1a;
    border-radius: 4px;
    padding: 8px 12px;
    color: #ffffff;
}
QComboBox:hover {
    border: 1px solid #333333;
    background-color: #1a1a1a;
}
"""

SUCCESS_MESSAGE_STYLE = """
QLabel {
    background-color: #001a00;
    border: 2px solid #00cc44;
    border-radius: 6px;
    padding: 16px;
    color: #00ff55;
    font-size: 14px;
}
"""

WARNING_MESSAGE_STYLE = """
QLabel {
    background-color: #1a0f00;
    border: 2px solid #ff9900;
    border-radius: 6px;
    padding: 16px;
    color: #ffaa00;
}
"""

INFO_MESSAGE_STYLE = """
QLabel {
    background-color: #001a33;
    border: 2px solid #0066cc;
    border-radius: 6px;
    padding: 16px;
    color: #0099ff;
    font-size: 13px;
}
"""

AUTO_MESSAGE_STYLE = """
QLabel {
    background-color: #1a001a;
    border: 2px solid #9900cc;
    border-radius: 6px;
    padding: 16px;
    color: #cc00ff;
    font-size: 13px;
}
"""

STAT_WIDGET_STYLE = """
QFrame {{
    background-color: #0a0a0a;
    border: 2px solid #{color_hex};
    border-radius: 8px;
    padding: 20px;
    min-width: 160px;
}}
"""

STAT_VALUE_STYLE = """
color: {color};
"""

FILE_DROP_NORMAL_STYLE = """
QLabel {
    border: 2px dashed #333333;
    border-radius: 6px;
    padding: 24px;
    background-color: #0d0d0d;
    color: #999999;
}
"""

FILE_DROP_HOVER_STYLE = """
QLabel {
    border: 2px dashed #0066cc;
    background-color: #001a33;
    color: #0099ff;
}
"""

# Couleurs pour les widgets de statistiques
STAT_COLORS = {
    "blue": "0066cc",
    "green": "00cc44", 
    "orange": "ff9900",
    "red": "ff3333",
    "purple": "9900cc"
}