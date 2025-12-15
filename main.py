import sys
import os
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox, QWidget
from PySide6.QtGui import QIcon
from core.config_manager import config_manager
# from gui.main_window import MainWindow # Placeholder

def run_setup(app):
    """
    Shows a dialog to select the data directory.
    Returns True if successful, False if cancelled.
    """
    dummy = QWidget() # Needed for parent
    
    msg = QMessageBox()
    msg.setWindowTitle("Welcome to Minecraft Manager")
    msg.setText("This seems to be your first time running the app.")
    msg.setInformativeText("Please choose a location to store all your Servers, Worlds, and Data.")
    msg.setIcon(QMessageBox.Information)
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    
    ret = msg.exec()
    
    if ret == QMessageBox.Cancel:
        return False
        
    directory = QFileDialog.getExistingDirectory(None, "Select Data Directory", os.getcwd())
    
    if directory:
        config_manager.set_data_path(directory)
        return True
    return False

def main():
    app = QApplication(sys.argv)
    
    # Set App Icon
    from core.config_manager import get_resource_path
    icon_path = get_resource_path(os.path.join("assets", "icon.png"))
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Apply Global Theme
    from gui.theme import Theme
    app.setStyleSheet(Theme.QSS)
    
    app.setApplicationName("Local MC Manager")
    
    if not config_manager.is_configured():
        success = run_setup(app)
        if not success:
            sys.exit(0)
            
    # Initialize Database
    try:
        from core.database import db_manager
        db_manager.connect()
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to initialize database: {e}")
        sys.exit(1)

    from gui.main_window import MainWindow
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
