from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                               QGroupBox, QFormLayout, QTextEdit, QHBoxLayout)
from PySide6.QtCore import Qt, QThread, Signal
import socket
import requests

class PublicIpWorker(QThread):
    finished = Signal(str)
    
    def run(self):
        try:
            response = requests.get('https://api.ipify.org', timeout=5)
            if response.status_code == 200:
                self.finished.emit(response.text)
            else:
                self.finished.emit("Error fetching IP")
        except Exception as e:
            self.finished.emit("Unavailable")

from core.config_manager import config_manager
import os

class PlayitManager(QThread):
    output_signal = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.data_path = str(config_manager.get_data_path())
        self.exe_path = os.path.join(self.data_path, "playit.exe")
        self.process = None
        self.is_running = True
        
    def run(self):
        import subprocess
        
        if not os.path.exists(self.exe_path):
            self.output_signal.emit("Error: playit.exe not found in global data.")
            return

        try:
            self.output_signal.emit(f"Starting Playit.gg agent (Global)...")
            
            # CREATE_NO_WINDOW = 0x08000000
            self.process = subprocess.Popen(
                [self.exe_path],
                cwd=self.data_path, # Run in global data dir to share playit.toml
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=0x08000000 
            )
            
            import re
            # Regex to strip ANSI escape codes
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            # Regex to strip control characters (like backspace \x08)
            control_chars = re.compile(r'[\x00-\x09\x0B-\x1F\x7F]')
            
            for line in self.process.stdout:
                if not self.is_running: break
                clean_line = ansi_escape.sub('', line)
                clean_line = control_chars.sub('', clean_line).strip()
                if clean_line:
                    self.output_signal.emit(clean_line)
                
            self.process.wait()
        except Exception as e:
            self.output_signal.emit(f"Error running agent: {e}")
            
    def stop(self):
        self.is_running = False
        if self.process:
            self.process.terminate()

class NetworkTab(QWidget):
    def __init__(self, server_data, parent=None):
        super().__init__(parent)
        self.server_data = server_data
        self.playit_thread = None
        
        layout = QVBoxLayout(self)
        
        # Connection Info
        conn_group = QGroupBox("Connection Information")
        conn_layout = QFormLayout(conn_group)
        
        self.local_ip_lbl = QLabel("Fetching...")
        self.public_ip_lbl = QLabel("Click 'Refresh' to fetch")
        self.port_lbl = QLabel(self.get_port())
        
        conn_layout.addRow("Server Port:", self.port_lbl)
        conn_layout.addRow("Local IP (LAN):", self.local_ip_lbl)
        conn_layout.addRow("Public IP (WAN):", self.public_ip_lbl)
        layout.addWidget(conn_group)
        
        # Refresh Button
        self.btn_refresh = QPushButton("Refresh IPs")
        self.btn_refresh.clicked.connect(self.refresh_ips)
        layout.addWidget(self.btn_refresh)
        
        # Tunneling Section (Playit.gg)
        tunnel_group = QGroupBox("Tunneling (Playit.gg)")
        tunnel_layout = QVBoxLayout(tunnel_group)
        
        self.status_lbl = QLabel("Status: Agent Stopped")
        self.status_lbl.setStyleSheet("font-weight: bold; color: #AAA;")
        
        btn_layout = QHBoxLayout()
        self.btn_download_agent = QPushButton("Download Agent")
        self.btn_download_agent.clicked.connect(self.download_agent)
        
        self.btn_start_tunnel = QPushButton("Start Tunnel")
        self.btn_start_tunnel.setStyleSheet("background-color: #4CAF50; color: white;")
        self.btn_start_tunnel.clicked.connect(self.toggle_tunnel)
        
        btn_layout.addWidget(self.btn_download_agent)
        btn_layout.addWidget(self.btn_start_tunnel)
        
        # Log Area
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFixedHeight(100)
        self.log_area.setPlaceholderText("Agent output (Check here for 'Claim URL')...")
        self.log_area.setStyleSheet("background: #111; color: #EEE; font-family: monospace; font-size: 11px;")

        # Help for existing users
        existing_layout = QHBoxLayout()
        self.btn_open_folder = QPushButton("Open Config Folder")
        self.btn_open_folder.setStyleSheet("background-color: #555;")
        self.btn_open_folder.clicked.connect(self.open_global_folder)
        
        help_lbl = QLabel("Agent and Config are now shared globally.")
        help_lbl.setStyleSheet("color: #888; font-style: italic; font-size: 11px;")
        
        existing_layout.addWidget(self.btn_open_folder)
        existing_layout.addWidget(help_lbl)
        
        tunnel_layout.addWidget(self.status_lbl)
        tunnel_layout.addLayout(btn_layout)
        tunnel_layout.addLayout(existing_layout)
        tunnel_layout.addWidget(self.log_area)
        
        layout.addWidget(tunnel_group)
        layout.addStretch()
        
        # Init
        self.refresh_local_ip()
        self.check_agent_exists()
        self.check_existing_process()

    def open_global_folder(self):
        import platform
        import subprocess
        path = str(config_manager.get_data_path())
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def check_agent_exists(self):
        path = str(config_manager.get_data_path())
        exe_path = os.path.join(path, "playit.exe")
        if os.path.exists(exe_path):
            self.btn_download_agent.setText("Agent Found (Global)")
            self.btn_download_agent.setEnabled(False)
        else:
            self.btn_download_agent.setText("Download Agent (v0.15.26)")
            self.btn_download_agent.setEnabled(True)

    def download_agent(self):
        import requests 
        url = "https://github.com/playit-cloud/playit-agent/releases/download/v0.15.26/playit-windows-x86_64-signed.exe"
        path = str(config_manager.get_data_path())
        target = os.path.join(path, "playit.exe")
        
        self.log_area.append("Downloading agent to global data folder...")
        try:
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                with open(target, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                self.log_area.append("Download complete!")
                self.check_agent_exists()
            else:
                self.log_area.append(f"Download failed: {r.status_code}")
        except Exception as e:
            self.log_area.append(f"Error: {e}")

    def toggle_tunnel(self):
        main_win = self.window()
        
        if main_win.playit_manager and main_win.playit_manager.isRunning():
            self.stop_process()
        else:
            # Check existence first
            path = str(config_manager.get_data_path())
            exe_path = os.path.join(path, "playit.exe")
            
            if not os.path.exists(exe_path):
                self.log_area.append("Error: Agent not found. Please click 'Download Agent' first.")
                import PySide6.QtWidgets
                from gui.dialogs import ModernMessageBox
                # Visual feedback
                ModernMessageBox.show_error(self, "Agent Missing", "Please download the Playit.gg agent first.")
                return

            # Start
            main_win.playit_manager = PlayitManager()
            # Connect log output
            main_win.playit_manager.output_signal.connect(self.update_log)
            main_win.playit_manager.start()
            
            self.update_ui_state(True)

    def stop_process(self):
        main_win = self.window()
        if main_win.playit_manager and main_win.playit_manager.isRunning():
            main_win.playit_manager.stop()
            main_win.playit_manager.wait()
        
        self.update_ui_state(False)
        
    def update_ui_state(self, is_running):
        if is_running:
            self.btn_start_tunnel.setText("Stop Tunnel")
            self.btn_start_tunnel.setStyleSheet("background-color: #F44336; color: white;")
            self.status_lbl.setText("Status: Agent Running")
        else:
            self.btn_start_tunnel.setText("Start Tunnel")
            self.btn_start_tunnel.setStyleSheet("background-color: #4CAF50; color: white;")
            self.status_lbl.setText("Status: Agent Stopped")

    def update_log(self, text):
        self.log_area.append(text)
        
    def check_existing_process(self):
        main_win = self.window()
        # Verify we actually got the MainWindow by checking for a known attribute
        if not hasattr(main_win, 'playit_manager'):
            # Fallback: Try walking up parent manually if window() is failing
            parent = self.parent()
            while parent:
                if hasattr(parent, 'playit_manager'):
                    main_win = parent
                    break
                parent = parent.parent()
        
        if hasattr(main_win, 'playit_manager') and main_win.playit_manager and main_win.playit_manager.isRunning():
            self.update_ui_state(True)
            # Reconnect signal to this new log area
            try: main_win.playit_manager.output_signal.disconnect()
            except: pass
            main_win.playit_manager.output_signal.connect(self.update_log)

    def get_port(self):
        port = "25565"
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
        return port

    def refresh_ips(self):
        self.refresh_local_ip()
        self.public_ip_lbl.setText("Fetching...")
        
        self.worker = PublicIpWorker()
        self.worker.finished.connect(self.update_public_ip)
        self.worker.start()

    def refresh_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            self.local_ip_lbl.setText(ip)
        except:
             self.local_ip_lbl.setText("127.0.0.1")

    def update_public_ip(self, ip):
        self.public_ip_lbl.setText(ip)
