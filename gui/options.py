from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, 
                               QPushButton, QGroupBox, QMessageBox, QHBoxLayout)
from core.database import db_manager

class LauncherOptions(QWidget):
    def __init__(self, server_id):
        super().__init__()
        self.server_id = server_id
        self.server_data = db_manager.get_server(server_id)
        
        layout = QVBoxLayout(self)
        
        group = QGroupBox("Startup Options")
        group.setStyleSheet("QGroupBox { border: 1px solid #444; margin-top: 10px; font-weight: bold; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        
        form = QFormLayout(group)
        
        self.java_input = QLineEdit(self.server_data.get('java_path', 'java'))
        self.java_input.setStyleSheet("padding: 5px; background: #333; color: white; border: 1px solid #555;")
        
        self.ram_min_input = QLineEdit(self.server_data.get('ram_min', '2048M'))
        self.ram_min_input.setPlaceholderText("e.g. 1024M or 1G")
        self.ram_min_input.setStyleSheet("padding: 5px; background: #333; color: white; border: 1px solid #555;")

        self.ram_max_input = QLineEdit(self.server_data.get('ram_max', '4096M'))
        self.ram_max_input.setPlaceholderText("e.g. 4096M or 4G")
        self.ram_max_input.setStyleSheet("padding: 5px; background: #333; color: white; border: 1px solid #555;")
        
        form.addRow("Java Path:", self.java_input)
        form.addRow("Min RAM (-Xms):", self.ram_min_input)
        form.addRow("Max RAM (-Xmx):", self.ram_max_input)
        
        layout.addWidget(group)
        
        # Save Button
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Save Launch Options")
        self.btn_save.setStyleSheet("background-color: #007ACC; color: white; padding: 8px; font-weight: bold;")
        self.btn_save.clicked.connect(self.save)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_save)
        
        layout.addLayout(btn_layout)
        layout.addStretch()

    def save(self):
        try:
            db_manager.update_server_options(
                self.server_id,
                self.java_input.text(),
                self.ram_min_input.text(),
                self.ram_max_input.text()
            )
            QMessageBox.information(self, "Saved", "Startup options saved! (Effect on next restart)")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
