from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, 
                               QSpinBox, QCheckBox, QPushButton, QScrollArea, QLabel, QMessageBox, QStackedWidget)
from PySide6.QtCore import Qt
import os

class PropertiesEditor(QWidget):
    def __init__(self, server_path):
        super().__init__()
        self.server_path = server_path
        self.file_path = os.path.join(server_path, "server.properties")
        self.properties = {}
        
        layout = QVBoxLayout(self)
        
        # Stack for switching views
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        
        # View 1: Missing File
        self.page_missing = QWidget()
        layout_missing = QVBoxLayout(self.page_missing)
        layout_missing.setSpacing(10)
        
        lbl_missing = QLabel("Server Properties not found.\nStart the server once to generate this file.")
        lbl_missing.setAlignment(Qt.AlignCenter)
        lbl_missing.setStyleSheet("color: #888; font-style: italic; margin: 20px;")
        
        btn_refresh = QPushButton("Check Again")
        btn_refresh.setFixedWidth(120)
        btn_refresh.clicked.connect(self.refresh_interface)
        btn_refresh.setStyleSheet("background-color: #555; padding: 5px;")
        
        layout_missing.addStretch()
        layout_missing.addWidget(lbl_missing)
        layout_missing.addWidget(btn_refresh, alignment=Qt.AlignCenter)
        layout_missing.addStretch()
        
        # View 2: Editor
        self.page_editor = QWidget()
        layout_editor = QVBoxLayout(self.page_editor)
        layout_editor.setContentsMargins(0,0,0,0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: transparent; border: none;")
        
        self.content_widget = QWidget()
        self.form_layout = QFormLayout(self.content_widget)
        self.form_layout.setLabelAlignment(Qt.AlignRight)
        
        scroll.setWidget(self.content_widget)
        layout_editor.addWidget(scroll)
        
        self.btn_save = QPushButton("Save Properties")
        self.btn_save.setStyleSheet("background-color: #007ACC; color: white; padding: 10px; font-weight: bold;")
        self.btn_save.clicked.connect(self.save_properties)
        layout_editor.addWidget(self.btn_save)
        
        # Add pages
        self.stack.addWidget(self.page_missing)
        self.stack.addWidget(self.page_editor)
        
        # Initial check
        self.refresh_interface()

    def showEvent(self, event):
        self.refresh_interface()
        super().showEvent(event)

    def refresh_interface(self):
        if os.path.exists(self.file_path):
            self.load_properties()
            self.create_fields()
            self.stack.setCurrentWidget(self.page_editor)
        else:
            self.stack.setCurrentWidget(self.page_missing)

    def load_properties(self):
        self.properties = {}
        if not os.path.exists(self.file_path):
            return

        with open(self.file_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        self.properties[key.strip()] = value.strip()

    def create_fields(self):
        # Clear existing rows
        while self.form_layout.rowCount() > 0:
            self.form_layout.removeRow(0)

        # Define fields we want to expose
        # format: (key, label, type, default)
        fields = [
            ("motd", "MOTD", "str", "A Minecraft Server"),
            ("server-port", "Port", "int", 25565),
            ("max-players", "Max Players", "int", 20),
            ("online-mode", "Online Mode", "bool", True),
            ("difficulty", "Difficulty", "str", "easy"),
            ("gamemode", "Gamemode", "str", "survival"),
            ("white-list", "Whitelist", "bool", False),
            ("pvp", "PvP", "bool", True),
            ("view-distance", "View Distance", "int", 10),
            ("simulation-distance", "Sim Distance", "int", 10),
            ("level-seed", "World Seed", "str", ""),
            ("enable-command-block", "Command Blocks", "bool", False),
        ]
        
        self.widgets = {}
        
        for key, label, ftype, default in fields:
            val = self.properties.get(key, str(default))
            
            if ftype == "bool":
                widget = QCheckBox()
                widget.setChecked(val.lower() == "true")
            elif ftype == "int":
                widget = QSpinBox()
                widget.setRange(0, 65535)
                # handle non-int garbage
                try: widget.setValue(int(val))
                except: widget.setValue(int(default))
            else:
                widget = QLineEdit(val)
                
            widget.setStyleSheet("background-color: #333; color: white; padding: 5px;")
            self.form_layout.addRow(QLabel(label + ":"), widget)
            self.widgets[key] = widget

    def save_properties(self):
        # Update self.properties from widgets
        for key, widget in self.widgets.items():
            if isinstance(widget, QCheckBox):
                val = "true" if widget.isChecked() else "false"
            elif isinstance(widget, QSpinBox):
                val = str(widget.value())
            else:
                val = widget.text()
            self.properties[key] = val
            
        try:
            content = "#Minecraft Server Properties\n#Edited by Local MC Manager\n"
            for k, v in self.properties.items():
                content += f"{k}={v}\n"
                
            with open(self.file_path, "w") as f:
                f.write(content)
            
            QMessageBox.information(self, "Success", "Properties saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {e}")
