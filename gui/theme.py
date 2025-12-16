from core.config_manager import get_resource_path
import os

class Theme:
    # Color Palette
    TEXT_PRIMARY = "#e0e0e0"
    TEXT_SECONDARY = "#aaaaaa"
    BG_DARK = "#1e1e1e"
    BG_PANEL = "#252526"
    ACCENT = "#007acc"
    BORDER = "#3e3e3e"
    
    BG_IMAGE_PATH = get_resource_path(os.path.join("assets", "background.png")).replace("\\", "/")
    
    ERROR = "#ff4444"
    
    BTN_ACCENT = f"""
        QPushButton {{
            background-color: {ACCENT};
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #0098ff;
        }}
        QPushButton:pressed {{
            background-color: #005c99;
        }}
    """
    QSS = f"""
    /* Global Styles */
    QWidget {{
        background-color: transparent;
        color: {TEXT_PRIMARY};
        font-family: 'Segoe UI', sans-serif;
        font-size: 14px;
    }}
    
    #CentralWidget {{
        border-image: url({BG_IMAGE_PATH}) 0 0 0 0 stretch stretch;
    }}

    /* Apply Minecraft Font to specific elements */
    QPushButton {{
        font-family: 'Mojang', sans-serif;
        letter-spacing: 1px;
        font-size: 13px;
    }}
    
    QLabel[class="title"] {{
        font-family: 'Mojang', sans-serif;
    }}

    /* Buttons */
    QPushButton {{
        background-color: {ACCENT};
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: #0098ff;
    }}
    QPushButton:pressed {{
        background-color: #005c99;
    }}
    QPushButton:disabled {{
        background-color: #333333;
        color: #777777;
    }}
    
    /* Sidebar Buttons (re-using main window logic usually, but here generally) */

    /* Input Fields */
    QLineEdit, QTextEdit, QPlainTextEdit {{
        background-color: #2d2d2d;
        border: 1px solid {BORDER};
        border-radius: 4px;
        padding: 6px;
        color: #f0f0f0;
    }}
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
        border-color: {ACCENT};
    }}

    /* Labels */
    QLabel {{
        color: {TEXT_PRIMARY};
    }}

    /* Scrollbars */
    QScrollBar:vertical {{
        border: none;
        background: {BG_DARK};
        width: 10px;
        margin: 0px 0px 0px 0px;
    }}
    QScrollBar::handle:vertical {{
        background: #424242;
        min-height: 20px;
        border-radius: 5px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        border: none;
        background: none;
    }}

    /* Lists and Tables */
    QListWidget, QTableWidget, QTreeWidget {{
        background-color: rgba(37, 37, 38, 0.8);
        border: 1px solid {BORDER};
        outline: none;
    }}
    QListWidget::item:selected, QTableWidget::item:selected, QTreeWidget::item:selected {{
        background-color: #37373d;
        color: white;
    }}
    QHeaderView::section {{
        background-color: #2d2d2d;
        padding: 4px;
        border: none;
        color: {TEXT_PRIMARY};
    }}
    """
