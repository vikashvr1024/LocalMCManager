class Theme:
    # Colors
    BG_DARK = "#18181b"       # Zinc 950
    BG_PANEL = "#27272a"      # Zinc 800
    ACCENT = "#6366f1"        # Indigo 500 (Vibrant Purple/Blue)
    ACCENT_HOVER = "#818cf8"  # Indigo 400
    TEXT_PRIMARY = "#f4f4f5"  # Zinc 100
    TEXT_SECONDARY = "#a1a1aa"# Zinc 400
    BORDER = "#3f3f46"        # Zinc 700
    SUCCESS = "#22c55e"       # Green 500
    ERROR = "#ef4444"         # Red 500
    
    # Global QSS
    QSS = f"""
    QMainWindow, QWidget {{
        background-color: {BG_DARK};
        color: {TEXT_PRIMARY};
        font-family: 'Segoe UI', sans-serif;
    }}
    
    QFrame {{
        border: none;
    }}
    
    /* Buttons */
    QPushButton {{
        background-color: {BG_PANEL};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 600;
    }}
    QPushButton:hover {{
        background-color: {BORDER};
    }}
    QPushButton:pressed {{
        background-color: {ACCENT};
        border-color: {ACCENT};
    }}
    
    /* Inputs */
    QLineEdit, QTextEdit, QPlainTextEdit {{
        background-color: {BG_PANEL};
        border: 1px solid {BORDER};
        border-radius: 4px;
        padding: 8px;
        color: {TEXT_PRIMARY};
        selection-background-color: {ACCENT};
    }}
    QLineEdit:focus, QTextEdit:focus {{
        border: 1px solid {ACCENT};
    }}
    
    /* Tab Widget */
    QTabWidget::pane {{
        border: 1px solid {BORDER};
        border-radius: 4px;
        background-color: {BG_DARK};
    }}
    QTabBar::tab {{
        background-color: {BG_DARK};
        color: {TEXT_SECONDARY};
        padding: 8px 20px;
        border-bottom: 2px solid transparent;
        margin-right: 4px;
    }}
    QTabBar::tab:selected {{
        color: {ACCENT};
        border-bottom: 2px solid {ACCENT};
    }}
    QTabBar::tab:hover {{
        color: {TEXT_PRIMARY};
    }}
    
    /* GroupBox */
    QGroupBox {{
        border: 1px solid {BORDER};
        border-radius: 6px;
        margin-top: 24px;
        font-weight: bold;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
    }}
    
    /* ScrollBar */
    QScrollBar:vertical {{
        background: {BG_DARK};
        width: 10px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {BORDER};
        min-height: 20px;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {ACCENT};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    """
    
    # Specific Styles
    BTN_ACCENT = f"""
        QPushButton {{
            background-color: {ACCENT};
            color: white;
            border: none;
        }}
        QPushButton:hover {{
            background-color: {ACCENT_HOVER};
        }}
    """
    
    BTN_ERROR = f"""
        QPushButton {{
            background-color: {ERROR};
            color: white;
            border: none;
        }}
        QPushButton:hover {{
            background-color: #f87171;
        }}
    """
