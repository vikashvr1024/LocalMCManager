from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QScrollArea, QFrame, QLabel, QGridLayout, QStyleOption, QStyle)
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtCore import Qt, Signal, QSize

class ServerCard(QFrame):
    clicked = Signal(int) # server_id
    delete_clicked = Signal(int)

    def __init__(self, server_data, status="OFFLINE"):
        super().__init__()
        self.server_id = server_data['id']
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(140)
        self.setFixedWidth(340) # Keep fixed width as per previous design, user snippet had min width but this is safer for grid
        
        # Load Background Image
        from core.config_manager import get_resource_path
        import os
        card_bg = get_resource_path(os.path.join("assets", "card.png")).replace("\\", "/")

        # Modern Card Style
        self.setStyleSheet(f"""
            QFrame {{
                background-image: url({card_bg});
                background-color: #2d2d2d;
                border: 2px solid transparent;
                border-radius: 12px;
            }}
            QFrame:hover {{
                background-color: #353535;
                border: 2px solid #00bcd4;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Header (Name + Delete)
        top_layout = QHBoxLayout()
        top_layout.setSpacing(8)
        
        name_lbl = QLabel(server_data['name'])
        name_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: white; border: none; background: transparent;")
        top_layout.addWidget(name_lbl)
        
        top_layout.addStretch()
        
        # Delete Button (Trash Icon)
        self.btn_del = QPushButton()
        self.btn_del.setFixedSize(32, 32)
        self.btn_del.setCursor(Qt.PointingHandCursor)
        self.btn_del.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(255, 68, 68, 0.2);
            }
            QPushButton:pressed {
                background-color: rgba(255, 68, 68, 0.3);
            }
        """)
        
        # Load Icon
        from core.config_manager import get_resource_path
        import os
        icon_path = get_resource_path(os.path.join("assets", "trash.png"))
        if os.path.exists(icon_path):
            self.btn_del.setIcon(QIcon(icon_path))
            self.btn_del.setIconSize(QSize(24, 24))
        else:
             self.btn_del.setText("DEL") # Fallback
             self.btn_del.setStyleSheet(self.btn_del.styleSheet() + "color: #ff4444; font-weight: bold; font-size: 10px;")

        self.btn_del.clicked.connect(self.on_delete)
        top_layout.addWidget(self.btn_del)
        
        layout.addLayout(top_layout)
        
        # Version
        ver_lbl = QLabel(f"{server_data['jar_type']} {server_data['version']}")
        ver_lbl.setStyleSheet("color: white; font-size: 14px; font-weight: bold; border: none; background: transparent;")
        layout.addWidget(ver_lbl)
        
        # Status
        status_lbl = QLabel(status)
        color = "#44ff44" if status == "ONLINE" else "#ff4444"
        if status == "STARTING": color = "#FFC107"
        if status == "RUNNING": color = "#44ff44" # Green for Running
        
        status_lbl.setStyleSheet(f"color: {color}; font-weight: bold; border: none; background: transparent;")
        layout.addWidget(status_lbl)

    def on_delete(self):
        self.delete_clicked.emit(self.server_id)

    def mousePressEvent(self, event):
        # Only emit clicked if we didn't click the delete button (handled by its own signal, 
        # but technically button consumes click so this usually works fine)
        self.clicked.emit(self.server_id)
        super().mousePressEvent(event)

class Dashboard(QWidget):
    create_server_clicked = Signal()
    server_selected = Signal(int)
    delete_requested = Signal(int)

    def __init__(self):
        super().__init__()
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QHBoxLayout()
        header.setContentsMargins(24, 24, 24, 0)
        
        title = QLabel("My Servers")
        title.setProperty("class", "title")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        add_btn = QPushButton("Create Server")
        add_btn.setFixedSize(220, 45)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                color: white;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
        """)
        add_btn.clicked.connect(self.create_server_clicked.emit)
        
        # Load Logo for Background
        from core.config_manager import get_resource_path
        import os
        logo_path = get_resource_path(os.path.join("assets", "minecraft_logo.png"))
        self.logo_pixmap = None
        if os.path.exists(logo_path):
             self.logo_pixmap = QPixmap(logo_path)
             # Scale "Big"
             if self.logo_pixmap.height() > 200:
                 self.logo_pixmap = self.logo_pixmap.scaledToHeight(200, Qt.SmoothTransformation)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(add_btn)
        
        self.main_layout.addLayout(header)
        
        # Server Grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; } QWidget { background: transparent; }")
        
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.grid_layout.setContentsMargins(0, 10, 0, 0) # Align with header
        self.grid_layout.setSpacing(20)
        
        scroll.setWidget(self.grid_container)
        self.main_layout.addWidget(scroll)

    def load_servers(self, servers, running_status=None):
        if running_status is None: running_status = {}
        
        # Clear existing
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Apply specific grid settings as requested
        self.grid_layout.setSpacing(20)
        self.grid_layout.setContentsMargins(24, 24, 24, 24)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        columns = 2 # Fixed 2 columns as requested
        
        for index, server in enumerate(servers):
            status = running_status.get(server['id'], "OFFLINE")
            card = ServerCard(server, status)
            card.clicked.connect(self.server_selected.emit)
            card.delete_clicked.connect(self.delete_requested.emit)
            
            row = index // columns
            col = index % columns
            self.grid_layout.addWidget(card, row, col, Qt.AlignTop)
            
        # Add stretch to empty columns to keep alignment if row not full
        for col in range(columns):
            self.grid_layout.setColumnStretch(col, 1)

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)
        
        if self.logo_pixmap:
            # Draw top center
            x = (self.width() - self.logo_pixmap.width()) // 2
            y = 10 
            p.drawPixmap(x, y, self.logo_pixmap)
