from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QGraphicsDropShadowEffect)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, QSize
from gui.theme import Theme
from core.config_manager import get_resource_path
import os

class ModernMessageBox(QDialog):
    def __init__(self, title, message, icon_type="info", parent=None, buttons=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set Window Icon
        icon_path = get_resource_path(os.path.join("assets", "icon.png"))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Container with shadow
        self.container = QFrame()
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.BG_PANEL};
                border: 1px solid {Theme.BORDER};
                border-radius: 10px;
            }}
        """)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(Qt.black)
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)
        
        container_layout = QVBoxLayout(self.container)
        
        # Header (Title + Close)
        header = QHBoxLayout()
        header.setSpacing(10) # Spacing between icon and title
        
        # Add Icon to Header
        if os.path.exists(icon_path):
            icon_lbl = QLabel()
            pixmap = QPixmap(icon_path)
            scaled_pixmap = pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_lbl.setPixmap(scaled_pixmap)
            icon_lbl.setStyleSheet("border: none; background: transparent;")
            header.addWidget(icon_lbl)
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-weight: bold; font-size: 14px; border: none;")
        
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(30, 30)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background: transparent; border: none; color: {Theme.TEXT_SECONDARY};
                font-size: 14px;
            }}
            QPushButton:hover {{ color: {Theme.ERROR}; }}
        """)
        btn_close.clicked.connect(self.reject)
        
        header.addWidget(title_lbl)
        header.addStretch()
        header.addWidget(btn_close)
        container_layout.addLayout(header)
        
        # Body (Text only for now, removing the "blue box" placeholder)
        body = QHBoxLayout()
        body.setContentsMargins(10, 10, 10, 20)
        
        msg_lbl = QLabel(message)
        msg_lbl.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: 13px; border: none;")
        msg_lbl.setWordWrap(True)
        
        body.addWidget(msg_lbl)
        container_layout.addLayout(body)
        
        # Footer (Buttons)
        footer = QHBoxLayout()
        footer.addStretch()
        
        if not buttons: buttons = ["OK"]
        
        for btn_text in buttons:
            btn = QPushButton(btn_text)
            btn.setFixedWidth(100)
            if btn_text in ["Delete", "Yes", "OK"]:
                btn.setStyleSheet(Theme.BTN_ACCENT)
                btn.clicked.connect(self.accept)
            else:
                btn.setStyleSheet(f"background-color: transparent; color: {Theme.TEXT_PRIMARY}; border: 1px solid {Theme.BORDER}; border-radius: 4px; padding: 5px;")
                btn.clicked.connect(self.reject)
                
            footer.addWidget(btn)
            
        container_layout.addLayout(footer)
        
        layout.addWidget(self.container)
        
    @staticmethod
    def show_info(parent, title, message):
        dlg = ModernMessageBox(title, message, "info", parent)
        dlg.exec()
        
    @staticmethod
    def show_error(parent, title, message):
        dlg = ModernMessageBox(title, message, "error", parent)
        dlg.exec()
        
    @staticmethod
    def show_success(parent, title, message):
        dlg = ModernMessageBox(title, message, "success", parent)
        dlg.exec()
