from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QTextEdit, QLineEdit, QLabel, QTabWidget, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QTextCursor

class ConsoleTab(QWidget):
    command_signal = Signal(str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Tools
        tools_layout = QHBoxLayout()
        
        self.btn_start = QPushButton("Start")
        self.btn_start.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 5px 15px;")
        
        self.btn_stop = QPushButton("Stop")
        self.btn_stop.setStyleSheet("background-color: #F44336; color: white; font-weight: bold; padding: 5px 15px;")
        self.btn_stop.setEnabled(False)
        
        self.status_lbl = QLabel("OFFLINE")
        self.status_lbl.setStyleSheet("color: #FF5555; font-weight: bold; margin-left: 10px;")
        
        tools_layout.addWidget(self.btn_start)
        tools_layout.addWidget(self.btn_stop)
        tools_layout.addWidget(self.status_lbl)
        tools_layout.addStretch()
        
        layout.addLayout(tools_layout)
        
        # Terminal
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setStyleSheet("background-color: #000000; color: #CCCCCC; font-family: Consolas, monospace;")
        layout.addWidget(self.terminal)
        
        # Input
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Enter command...")
        self.input_line.setStyleSheet("background-color: #333; color: white; padding: 5px;")
        self.input_line.returnPressed.connect(self.send_command)
        layout.addWidget(self.input_line)

    def send_command(self):
        cmd = self.input_line.text()
        if cmd:
            self.command_signal.emit(cmd)
            self.input_line.clear()
            # Echo for now
            self.append_log(f"> {cmd}")

    def append_log(self, text):
        self.terminal.append(text)

class ServerPage(QWidget):
    def __init__(self, server_id, parent=None):
        super().__init__(parent)
        self.server_id = server_id
        
        # Load data
        from core.database import db_manager
        self.server_data = db_manager.get_server(server_id)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        
        # Header (Back button + Title)
        header = QHBoxLayout()
        self.btn_back = QPushButton("<- Back")
        self.btn_back.setFixedSize(80, 30)
        self.btn_back.setStyleSheet("background-color: #444; color: white; border: none;")
        
        self.title_lbl = QLabel(self.server_data['name'])
        self.title_lbl.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        # IP Info
        port = "25565"
        lan_ip = "127.0.0.1"
        try:
            import socket
            # Try to get actual LAN IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            lan_ip = s.getsockname()[0]
            s.close()
        except:
            try:
                lan_ip = socket.gethostbyname(socket.gethostname())
            except: pass

        try:
             import os
             props_path = os.path.join(self.server_data['path'], "server.properties")
             if os.path.exists(props_path):
                 with open(props_path, "r") as f:
                     for line in f:
                         if line.strip().startswith("server-port="):
                             port = line.split("=")[1].strip()
                             break
        except: pass
        
        self.info_lbl = QLabel(f"IP: {lan_ip}:{port}")
        self.info_lbl.setStyleSheet("color: #AAA; margin-left: 15px; font-size: 14px;")
        
        header.addWidget(self.btn_back)
        header.addWidget(self.title_lbl)
        header.addWidget(self.info_lbl)
        header.addStretch()
        layout.addLayout(header)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #444; }
            QTabBar::tab { background: #333; color: #AAA; padding: 8px 20px; }
            QTabBar::tab:selected { background: #444; color: white; }
        """)
        
        self.console_tab = ConsoleTab()
        self.tabs.addTab(self.console_tab, "Console")
        # Files Tab
        from gui.file_manager import FileManager
        self.file_manager = FileManager(self.server_data['path'])
        self.tabs.addTab(self.file_manager, "Files")


        # Options Tab (Properties + Launch)
        from PySide6.QtWidgets import QWidget
        # QVBoxLayout is already imported at module level
        options_widget = QWidget()
        options_layout = QVBoxLayout(options_widget)

        from gui.properties import PropertiesEditor
        from gui.options import LauncherOptions
        
        self.launcher_options = LauncherOptions(self.server_id)
        self.properties_editor = PropertiesEditor(self.server_data['path'])
        
        options_layout.addWidget(self.launcher_options)
        options_layout.addWidget(self.properties_editor)
        
        self.tabs.addTab(options_widget, "Options")

        
        from gui.network import NetworkTab
        self.network_tab = NetworkTab(self.server_data, parent=self)
        self.tabs.addTab(self.network_tab, "Network")
        
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        layout.addWidget(self.tabs)
        
        # Initialize Backend
        self.init_process()

    def on_tab_changed(self, index):
        # Refresh properties when Options tab (index 2) is selected
        # Indices: 0=Console, 1=Files, 2=Options, 3=Network
        if index == 2:
            if hasattr(self, 'properties_editor'):
                self.properties_editor.refresh_interface()

    def set_server_name(self, name):
        # Override handled in init now
        pass

    def cleanup(self):
        # Stop Server
        if hasattr(self, 'process'):
            self.process.kill_server() # Force kill for fast exit
            self.process.deleteLater()
            
        # Stop Playit
        if hasattr(self, 'network_tab'):
            self.network_tab.stop_process()

    def init_process(self):
        from core.server_process import ServerProcess
        import os
        
        path = self.server_data['path']
        if not os.path.exists(os.path.join(path, "server.jar")):
            self.console_tab.append_log("WARNING: server.jar not found! Please download it.")
            self.console_tab.input_line.setEnabled(False)
            self.console_tab.btn_start.setText("Download JAR")
            self.console_tab.btn_start.clicked.connect(self.start_download)
        else:
            self.setup_process()
            
    def setup_process(self):
        from core.server_process import ServerProcess
        from core.database import db_manager
        
        self.server_data = db_manager.get_server(self.server_id)
        
        main_win = self.window()
        existing_process = main_win.running_servers.get(self.server_id)
        
        if existing_process:
            self.process = existing_process
        else:
            self.process = ServerProcess(
                server_directory=self.server_data['path'],
                jar_name="server.jar",
                java_path=self.server_data.get('java_path', 'java'),
                ram_min=self.server_data.get('ram_min', '2048M'),
                ram_max=self.server_data.get('ram_max', '4096M')
            )
            main_win.running_servers[self.server_id] = self.process
        
        # Reconnect Signals (Disconnect old first to avoid dupes if page reloaded)
        try: self.process.log_output.disconnect()
        except: pass
        try: self.process.status_changed.disconnect()
        except: pass
        try: self.process.finished.disconnect()
        except: pass
        
        # Connect UI Buttons
        try: self.console_tab.btn_start.clicked.disconnect() 
        except: pass
        try: self.console_tab.btn_stop.clicked.disconnect() 
        except: pass
        
        self.console_tab.btn_start.setText("Start")
        self.console_tab.btn_start.clicked.connect(self.process.start_server)
        self.console_tab.btn_stop.clicked.connect(self.process.stop_server)
        
        self.console_tab.command_signal.connect(self.process.write_command)
        
        if hasattr(self.process, 'log_history') and self.process.log_history:
            # Load full history. Since append_log appends, clearing first might be safer if we reuse widgets, 
            # but console_tab is new here.
            full_log = "\n".join(self.process.log_history)
            self.console_tab.terminal.setPlainText(full_log)
            self.console_tab.terminal.moveCursor(QTextCursor.End)
        
        self.process.log_output.connect(self.console_tab.append_log)
        self.process.status_changed.connect(self.update_status)
        # self.process.finished.connect(self.handle_finished) # We handle finish via status change mostly
        
        # Sync Initial Status
        if hasattr(self.process, 'get_current_status'):
             self.update_status(self.process.get_current_status())
        
    def update_status(self, status):
        self.console_tab.status_lbl.setText(status)
        
        if status == "ONLINE":
            self.console_tab.status_lbl.setStyleSheet("color: #4CAF50; font-weight: bold; margin-left: 10px;")
            self.set_buttons(start=False, stop=True)
            self.console_tab.btn_stop.setText("Stop")
            
        elif status == "OFFLINE":
             self.console_tab.status_lbl.setStyleSheet("color: #FF5555; font-weight: bold; margin-left: 10px;")
             self.set_buttons(start=True, stop=False)
             self.console_tab.btn_stop.setText("Stop")
             
        elif status == "STARTING":
            self.console_tab.status_lbl.setStyleSheet("color: #FFC107; font-weight: bold; margin-left: 10px;")
            self.set_buttons(start=False, stop=True) # stop allowed to kill
            
        elif status in ["STOPPING", "RESTARTING"]:
            self.console_tab.status_lbl.setStyleSheet("color: #FFC107; font-weight: bold; margin-left: 10px;")
            self.set_buttons(start=False, stop=True) # Enable stop for force kill
            self.console_tab.btn_stop.setText("Force Kill")

    def set_buttons(self, start, stop):
        self.console_tab.btn_start.setEnabled(start)
        self.console_tab.btn_stop.setEnabled(stop)
             
    def start_download(self):
        self.console_tab.append_log("Started Downloading... (UI will freeze briefly, threading WIP)")
        from core.downloader import downloader
        import os
        import shutil
        import datetime
        
        jar_type = self.server_data.get('jar_type', 'Paper')
        version = self.server_data.get('version', '1.20.4')
        
        url = downloader.get_download_url(jar_type, version)
        
        if not url:
            self.console_tab.append_log(f"Error: Could not find download for {jar_type} {version}")
            return

        target = os.path.join(self.server_data['path'], "server.jar")
        
        # Backup existing if any
        if os.path.exists(target):
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            backup_name = f"server.jar.backup-{timestamp}"
            try:
                shutil.move(target, os.path.join(self.server_data['path'], backup_name))
                self.console_tab.append_log(f"Backed up old jar to {backup_name}")
            except Exception as e:
                self.console_tab.append_log(f"Backup failed: {e}")

        success = downloader.download_jar(url, target)
        
        if success:
            self.console_tab.append_log("Download Complete!")
            # Check EULA
            eula_path = os.path.join(self.server_data['path'], "eula.txt")
            if not os.path.exists(eula_path):
                with open(eula_path, "w") as f:
                    f.write("eula=true")
                self.console_tab.append_log("Accepted EULA.")
            
            self.setup_process()
            self.console_tab.input_line.setEnabled(True)
        else:
            self.console_tab.append_log("Download Failed.")
