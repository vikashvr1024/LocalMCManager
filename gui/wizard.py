from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                               QComboBox, QDialogButtonBox, QMessageBox)
from core.database import db_manager
import os
from core.config_manager import config_manager

class CreateServerWizard(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Server")
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #252526; color: white;")
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("My Survival Server")
        self.name_input.setStyleSheet("padding: 5px; background-color: #333; border: 1px solid #555;")
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Vanilla", "Paper", "Purpur", "Fabric", "Spigot", "Forge"])
        self.type_combo.setStyleSheet("padding: 5px; background-color: #333; border: 1px solid #555;")
        self.type_combo.currentTextChanged.connect(self.update_versions)
        
        self.version_combo = QComboBox()
        self.version_combo.setEditable(True)
        self.version_combo.setStyleSheet("padding: 5px; background-color: #333; border: 1px solid #555;")
        
        form_layout.addRow("Server Name:", self.name_input)
        form_layout.addRow("Software:", self.type_combo)
        form_layout.addRow("Version:", self.version_combo)
        
        layout.addLayout(form_layout)
        
        # Initial populate
        self.update_versions(self.type_combo.currentText())

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def update_versions(self, loader_type):
        from core.downloader import downloader
        # This acts on the UI thread, might freeze slightly if checking net.
        # Ideally run in background, but for now catch errors.
        self.version_combo.clear()
        self.version_combo.addItem("Fetching...")
        
        # processEvents to show "Fetching..."?
        # A proper async way is better, but doing sync in stub for simplicity:
        try:
            # We will use a separate QTimer or just do it (fast enough usually)
            versions = downloader.get_versions(loader_type)
            self.version_combo.clear()
            self.version_combo.addItems(versions)
        except:
             self.version_combo.clear()
             self.version_combo.addItems(["Error Fetching"])

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "type": self.type_combo.currentText(),
            "version": self.version_combo.currentText()
        }

    def accept(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Invalid Input", "Server name cannot be empty.")
            return

        # Prepare path
        safe_name = "".join([c for c in name if c.isalpha() or c.isdigit() or c==' ']).strip()
        server_path = os.path.join(config_manager.get_data_path(), safe_name)
        
        if os.path.exists(server_path):
             QMessageBox.warning(self, "Exists", "A server with this name (folder) already exists.")
             return

        # Create folder
        try:
            os.makedirs(server_path)
            
            # EULA Auto-Accept
            with open(os.path.join(server_path, "eula.txt"), "w") as f:
                f.write("eula=true")

            # Save to DB
            server_id = db_manager.add_server(
                name=name,
                path=server_path,
                jar_type=self.type_combo.currentText(),
                version=self.version_combo.currentText()
            )
            
            # We don't download here to avoid blocking close.
            # MainWindow/Console will see missing jar and prompt/auto download.
            
            QMessageBox.information(self, "Success", f"Server '{name}' created!\nGo to the Console tab to download the server jar and start it.")
            super().accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create server: {e}")
