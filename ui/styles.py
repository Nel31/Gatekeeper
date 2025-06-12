"""
Styles CSS compatibles avec PyQt6 - Thème sombre moderne
"""

MAIN_STYLE = """
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #0f0f0f, stop:0.5 #1a1a1a, stop:1 #0f0f0f);
    color: #ffffff;
}

QWidget {
    background-color: transparent;
    color: #ffffff;
}

QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.15),
        stop:1 rgba(255, 255, 255, 0.05));
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    padding: 12px 24px;
    font-weight: 600;
    font-size: 13px;
    color: #ffffff;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.25),
        stop:1 rgba(255, 255, 255, 0.15));
    border: 1px solid rgba(255, 255, 255, 0.3);
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.1),
        stop:1 rgba(255, 255, 255, 0.05));
}

QPushButton#primaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #4fc3f7, stop:0.5 #29b6f6, stop:1 #0288d1);
    border: 2px solid #4fc3f7;
    color: #ffffff;
    font-size: 14px;
    font-weight: 700;
}

QPushButton#primaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #81d4fa, stop:0.5 #4fc3f7, stop:1 #29b6f6);
    border: 2px solid #81d4fa;
}

QPushButton#primaryButton:disabled {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.5);
}

QPushButton#successButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #81c784, stop:0.5 #66bb6a, stop:1 #4caf50);
    border: 2px solid #81c784;
    color: #ffffff;
}

QPushButton#successButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #a5d6a7, stop:0.5 #81c784, stop:1 #66bb6a);
    border: 2px solid #a5d6a7;
}

QGroupBox {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.1),
        stop:1 rgba(255, 255, 255, 0.05));
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 16px;
    margin-top: 20px;
    padding-top: 20px;
    font-weight: 700;
    font-size: 14px;
    color: #4fc3f7;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 20px;
    padding: 8px 16px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #4fc3f7, stop:1 #29b6f6);
    border-radius: 12px;
    color: #ffffff;
    font-weight: 700;
}

QLineEdit {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.1),
        stop:1 rgba(255, 255, 255, 0.05));
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 13px;
    color: #ffffff;
}

QLineEdit:focus {
    border: 2px solid #4fc3f7;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(79, 195, 247, 0.15),
        stop:1 rgba(79, 195, 247, 0.05));
}

QProgressBar {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    text-align: center;
    height: 24px;
    color: #ffffff;
    font-weight: 600;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4fc3f7, stop:0.5 #29b6f6, stop:1 #0288d1);
    border-radius: 11px;
}

QTableWidget {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.08),
        stop:1 rgba(255, 255, 255, 0.03));
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 12px;
    gridline-color: rgba(255, 255, 255, 0.1);
    color: #ffffff;
    alternate-background-color: rgba(255, 255, 255, 0.05);
}

QTableWidget::item {
    padding: 8px;
    border: none;
}

QTableWidget::item:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(79, 195, 247, 0.3),
        stop:1 rgba(41, 182, 246, 0.3));
    color: #ffffff;
}

QHeaderView::section {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.15),
        stop:1 rgba(255, 255, 255, 0.08));
    border: none;
    border-right: 1px solid rgba(255, 255, 255, 0.1);
    padding: 12px 8px;
    font-weight: 700;
    color: #4fc3f7;
}

QTabWidget::pane {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.1),
        stop:1 rgba(255, 255, 255, 0.05));
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    margin-top: 10px;
}

QTabWidget::tab-bar {
    alignment: center;
}

QTabBar::tab {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.1),
        stop:1 rgba(255, 255, 255, 0.05));
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-bottom: none;
    border-radius: 8px 8px 0 0;
    padding: 12px 20px;
    margin-right: 2px;
    color: rgba(255, 255, 255, 0.8);
    font-weight: 600;
}

QTabBar::tab:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #4fc3f7, stop:1 #29b6f6);
    color: #ffffff;
    border: 2px solid #4fc3f7;
}

QTabBar::tab:hover:!selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.2),
        stop:1 rgba(255, 255, 255, 0.1));
    color: #ffffff;
}

QListWidget {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.08),
        stop:1 rgba(255, 255, 255, 0.03));
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 10px;
    color: #ffffff;
}

QListWidget::item {
    padding: 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

QListWidget::item:selected {
    background: rgba(79, 195, 247, 0.3);
}

QTextEdit {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.1),
        stop:1 rgba(255, 255, 255, 0.05));
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 10px;
    padding: 12px;
    color: #ffffff;
}

QTextEdit:focus {
    border: 2px solid #4fc3f7;
}

QScrollBar:vertical {
    background: rgba(255, 255, 255, 0.1);
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4fc3f7, stop:1 #29b6f6);
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #81d4fa, stop:1 #4fc3f7);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: rgba(255, 255, 255, 0.1);
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #4fc3f7, stop:1 #29b6f6);
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #81d4fa, stop:1 #4fc3f7);
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QMenuBar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.1),
        stop:1 rgba(255, 255, 255, 0.05));
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    color: #ffffff;
    padding: 4px;
}

QMenuBar::item {
    background: transparent;
    padding: 8px 16px;
    border-radius: 8px;
    margin: 2px;
}

QMenuBar::item:selected {
    background: rgba(79, 195, 247, 0.3);
    color: #ffffff;
}

QMenu {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.15),
        stop:1 rgba(255, 255, 255, 0.08));
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 10px;
    color: #ffffff;
    padding: 8px;
}

QMenu::item {
    padding: 10px 20px;
    border-radius: 6px;
    margin: 2px;
}

QMenu::item:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(79, 195, 247, 0.4),
        stop:1 rgba(41, 182, 246, 0.4));
    color: #ffffff;
}

QStatusBar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.08),
        stop:1 rgba(255, 255, 255, 0.03));
    border-top: 1px solid rgba(255, 255, 255, 0.2);
    color: rgba(255, 255, 255, 0.9);
    padding: 8px;
}

QComboBox {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.1),
        stop:1 rgba(255, 255, 255, 0.05));
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 10px;
    padding: 10px 16px;
    color: #ffffff;
}

QComboBox:hover {
    border: 1px solid rgba(79, 195, 247, 0.5);
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(79, 195, 247, 0.15),
        stop:1 rgba(79, 195, 247, 0.05));
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #4fc3f7;
    margin-right: 10px;
}

QComboBox QAbstractItemView {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.15),
        stop:1 rgba(255, 255, 255, 0.08));
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 10px;
    color: #ffffff;
    selection-background-color: rgba(79, 195, 247, 0.3);
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
    border: 2px solid rgba(255, 255, 255, 0.3);
    background: rgba(255, 255, 255, 0.1);
}

QRadioButton::indicator:checked {
    border: 2px solid #4fc3f7;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #4fc3f7, stop:1 #29b6f6);
}

QRadioButton::indicator:hover {
    border: 2px solid rgba(79, 195, 247, 0.6);
    background: rgba(79, 195, 247, 0.1);
}
"""

STEP_ACTIVE_STYLE = """
QLabel {
    border-radius: 15px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #4fc3f7, stop:0.5 #29b6f6, stop:1 #0288d1);
    color: #ffffff;
    font-weight: 700;
    font-size: 14px;
    border: 2px solid #4fc3f7;
}
"""

STEP_COMPLETED_STYLE = """
QLabel {
    border-radius: 15px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #81c784, stop:0.5 #66bb6a, stop:1 #4caf50);
    color: #ffffff;
    font-weight: 700;
    font-size: 14px;
    border: 2px solid #81c784;
}
"""

STEP_INACTIVE_STYLE = """
QLabel {
    border-radius: 15px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.1),
        stop:1 rgba(255, 255, 255, 0.05));
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: rgba(255, 255, 255, 0.7);
    font-weight: 600;
    font-size: 14px;
}
"""

STEP_TEXT_ACTIVE_STYLE = """
QLabel {
    color: #4fc3f7;
    font-weight: 700;
    font-size: 13px;
}
"""

STEP_TEXT_COMPLETED_STYLE = """
QLabel {
    color: #81c784;
    font-weight: 600;
    font-size: 13px;
}
"""

STEP_TEXT_INACTIVE_STYLE = """
QLabel {
    color: rgba(255, 255, 255, 0.7);
    font-weight: 500;
    font-size: 13px;
}
"""

VALID_ICON_STYLE = """
color: #81c784; 
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
    border: 2px solid rgba(255, 255, 255, 0.3);
    background: rgba(255, 255, 255, 0.1);
}
QRadioButton::indicator:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #4fc3f7, stop:1 #29b6f6);
    border: 2px solid #4fc3f7;
}
QRadioButton::indicator:hover {
    border: 2px solid rgba(79, 195, 247, 0.6);
    background: rgba(79, 195, 247, 0.1);
}
"""

COMBO_BOX_STYLE = """
QComboBox {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.1),
        stop:1 rgba(255, 255, 255, 0.05));
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    padding: 8px 12px;
    color: #ffffff;
}
QComboBox:hover {
    border: 1px solid rgba(79, 195, 247, 0.5);
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(79, 195, 247, 0.15),
        stop:1 rgba(79, 195, 247, 0.05));
}
"""

SUCCESS_MESSAGE_STYLE = """
QLabel {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(129, 199, 132, 0.2),
        stop:1 rgba(76, 175, 80, 0.1));
    border: 2px solid #81c784;
    border-radius: 12px;
    padding: 16px;
    color: #81c784;
    font-size: 14px;
}
"""

WARNING_MESSAGE_STYLE = """
QLabel {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 193, 7, 0.2),
        stop:1 rgba(255, 152, 0, 0.1));
    border: 2px solid #ffc107;
    border-radius: 12px;
    padding: 16px;
    color: #ffb74d;
}
"""

INFO_MESSAGE_STYLE = """
QLabel {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(79, 195, 247, 0.2),
        stop:1 rgba(41, 182, 246, 0.1));
    border: 2px solid #4fc3f7;
    border-radius: 12px;
    padding: 16px;
    color: #4fc3f7;
    font-size: 13px;
}
"""

AUTO_MESSAGE_STYLE = """
QLabel {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(156, 39, 176, 0.2),
        stop:1 rgba(142, 36, 170, 0.1));
    border: 2px solid #9c27b0;
    border-radius: 12px;
    padding: 16px;
    color: #ba68c8;
    font-size: 13px;
}
"""

STAT_WIDGET_STYLE = """
QFrame {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.15),
        stop:1 rgba(255, 255, 255, 0.05));
    border: 2px solid rgba({color_rgb}, 0.5);
    border-radius: 16px;
    padding: 20px;
    min-width: 160px;
}}
"""

STAT_VALUE_STYLE = """
color: {color};
"""

FILE_DROP_NORMAL_STYLE = """
QLabel {
    border: 2px dashed rgba(255, 255, 255, 0.3);
    border-radius: 12px;
    padding: 24px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.08),
        stop:1 rgba(255, 255, 255, 0.03));
    color: rgba(255, 255, 255, 0.8);
}
"""

FILE_DROP_HOVER_STYLE = """
QLabel {
    border: 2px dashed #4fc3f7;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(79, 195, 247, 0.2),
        stop:1 rgba(79, 195, 247, 0.1));
    color: #4fc3f7;
}
"""

# Couleurs pour les widgets de statistiques
STAT_COLORS = {
    "blue": "79, 195, 247",
    "green": "129, 199, 132", 
    "orange": "255, 183, 77",
    "red": "239, 83, 80",
    "purple": "186, 104, 200"
}