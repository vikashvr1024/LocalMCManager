from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QStackedWidget, QLabel, QFrame)
from PySide6.QtCore import Qt, QSize

from gui.theme import Theme

class SidebarButton(QPushButton):
    def __init__(self, text, icon_name=None, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setFixedHeight(45)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding-left: 24px;
                border: none;
                background-color: transparent;
                color: {Theme.TEXT_SECONDARY};
                font-size: 14px;
                border-radius: 0px;
            }}
            QPushButton:checked {{
                background-color: {Theme.BG_DARK};
                color: {Theme.ACCENT};
                border-left: 3px solid {Theme.ACCENT};
            }}
            QPushButton:hover:!checked {{
                background-color: {Theme.BG_DARK};
                color: {Theme.TEXT_PRIMARY};
            }}
        """)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Local MC Manager")
        self.resize(1100, 750)
        # Background handled by Global QSS
        
        # Main Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Process Management (Global)
        self.running_servers = {} # {server_id: ServerProcess}
        self.playit_manager = None
        
        # Sidebar
        self.create_sidebar()
        
        # Content Area
        self.content_area = QStackedWidget()
        self.main_layout.addWidget(self.content_area)
        
        # Initial Page
        self.init_home_page()

    def create_sidebar(self):
        self.sidebar_container = QFrame()
        self.sidebar_container.setFixedWidth(220)
        self.sidebar_container.setStyleSheet(f"background-color: {Theme.BG_PANEL}; border-right: 1px solid {Theme.BORDER};")
        
        self.sidebar_layout = QVBoxLayout(self.sidebar_container)
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_layout.setSpacing(5)
        
        # Title
        title_label = QLabel("MC MANAGER")
        title_label.setFixedHeight(60)
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title_label.setStyleSheet(f"font-weight: 900; font-size: 18px; color: {Theme.ACCENT}; letter-spacing: 1px; padding-left: 24px;")
        self.sidebar_layout.addWidget(title_label)
        
        # Navigation Buttons
        self.btn_dashboard = SidebarButton("Dashboard")
        
        self.sidebar_layout.addWidget(self.btn_dashboard)
        
        self.sidebar_layout.addStretch()
        
        # Version info
        version_label = QLabel("v1.0.0-beta.1")
        version_label.setAlignment(Qt.AlignCenter)
        self.sidebar_layout.addWidget(version_label)
        
        self.main_layout.addWidget(self.sidebar_container)

    def init_home_page(self):
        from gui.dashboard import Dashboard
        from gui.wizard import CreateServerWizard
        from core.database import db_manager

        self.dashboard = Dashboard()
        self.dashboard.create_server_clicked.connect(self.open_wizard)
        self.dashboard.server_selected.connect(self.open_server_page)
        self.dashboard.delete_requested.connect(self.handle_delete_server)
        
        self.content_area.addWidget(self.dashboard)
        self.refresh_dashboard()

        # Connect Sidebar
        # Connect Sidebar
        self.btn_dashboard.clicked.connect(lambda: self.content_area.setCurrentWidget(self.dashboard))

    def refresh_dashboard(self):
        from core.database import db_manager
        servers = db_manager.get_all_servers()
        
        # Build status map
        status_map = {}
        if hasattr(self, 'running_servers'):
            from PySide6.QtCore import QProcess
            for s_id, process in self.running_servers.items():
                if process.process.state() == QProcess.Running:
                    status_map[s_id] = "ONLINE"
                elif process.process.state() == QProcess.Starting:
                    status_map[s_id] = "STARTING"
                else:
                    status_map[s_id] = "OFFLINE"
        
        self.dashboard.load_servers(servers, status_map)

    def open_wizard(self):
        from gui.wizard import CreateServerWizard
        wizard = CreateServerWizard(self)
        if wizard.exec():
            # Refresh list
            self.refresh_dashboard()
            
    def open_server_page(self, server_id):
        from gui.console import ServerPage
        from core.database import db_manager
        
        # Fetch server details
        server = db_manager.get_server(server_id)
        
        if server:
            self.server_page = ServerPage(server_id, parent=self)
            self.server_page.set_server_name(server['name'])
            self.server_page.btn_back.clicked.connect(self.go_home)
            
            # Switch view
            self.content_area.addWidget(self.server_page)
            self.content_area.setCurrentWidget(self.server_page)
            
            # Update sidebar selection (optional logic)
            self.btn_dashboard.setChecked(False)

    def go_home(self):
        if hasattr(self, 'server_page'):
             # Don't cleanup processes here! User wants them backgrounded.
             self.content_area.removeWidget(self.server_page)
             self.server_page.deleteLater()
             del self.server_page
             
        self.content_area.setCurrentWidget(self.dashboard)
        self.btn_dashboard.setChecked(True)
        self.refresh_dashboard()

    def closeEvent(self, event):
        # Stop all servers
        for s_id, process in self.running_servers.items():
            if process:
                process.kill_server()
        
        # Stop Playit
        if self.playit_manager:
            self.playit_manager.stop()
            self.playit_manager.wait()
            
        event.accept()

    def handle_delete_server(self, server_id):
        from gui.dialogs import ModernMessageBox
        from core.database import db_manager
        import shutil
        import os
        
        server = db_manager.get_server(server_id)
        if not server: return
        
        # Confirm
        dlg = ModernMessageBox(
            "Delete Server", 
            f"Are you sure you want to delete '{server['name']}'?\nThis will permanently delete all files.",
            "warning", self, buttons=["Cancel", "Delete"]
        )
        if not dlg.exec(): return
        
        # 1. Stop Server
        process = self.running_servers.get(server_id)
        if process:
            process.kill_server()
            del self.running_servers[server_id]
            
        # 2. Delete Files
        try:
            if os.path.exists(server['path']):
                shutil.rmtree(server['path'])
        except Exception as e:
            ModernMessageBox.show_error(self, "Error", f"Failed to delete files: {e}")
            return

        # 3. Delete from DB
        db_manager.delete_server(server_id)
        
        # 4. Refresh
        self.refresh_dashboard()
        ModernMessageBox.show_success(self, "Deleted", "Server deleted successfully.")


