from PySide6.QtCore import QObject, Signal, QProcess, QByteArray
import os

class ServerProcess(QObject):
    log_output = Signal(str)
    status_changed = Signal(str) # STARTING, ONLINE, STOPPING, OFFLINE
    finished = Signal()

    def __init__(self, server_directory, jar_name="server.jar", java_path="java", ram_min="1024M", ram_max="2048M"):
        super().__init__()
        self.server_dir = server_directory
        self.jar_name = jar_name
        self.java_path = java_path
        self.ram_min = ram_min
        self.ram_max = ram_max
        self.is_restarting = False
        
        self.process = QProcess()
        self.process.setProgram(self.java_path)
        self.process.setWorkingDirectory(self.server_dir)
        
        self.log_history = [] # Buffer for full logs
        
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.stateChanged.connect(self.handle_state_change)
        self.process.finished.connect(self.handle_finished)
        
        self.current_status = "OFFLINE"

    def get_current_status(self):
        return self.current_status

    def start_server(self):
        self.is_restarting = False
        if self.process.state() != QProcess.NotRunning:
            self.log_output.emit("Warning: Process is already running.")
            return

        if not os.path.exists(os.path.join(self.server_dir, self.jar_name)):
            error_msg = "Error: server.jar not found!"
            self.log_output.emit(error_msg)
            self.log_history.append(error_msg)
            return
        
        # Auto-Accept EULA
        try:
            with open(os.path.join(self.server_dir, "eula.txt"), "w") as f:
                f.write("eula=true\n")
            msg = "Enforced EULA acceptance."
            self.log_output.emit(msg)
            self.log_history.append(msg)
        except Exception as e:
            msg = f"Warning: Could not write eula.txt: {e}"
            self.log_output.emit(msg)
            self.log_history.append(msg)

        # Arguments
        args = [
            f"-Xms{self.ram_min}",
            f"-Xmx{self.ram_max}",
            "-jar",
            self.jar_name,
            "nogui"
        ]
        self.process.setArguments(args)
        
        msg = f"Starting server in {self.server_dir}..."
        self.log_output.emit(msg)
        self.log_history.append(msg)
        self.process.start()
        self.current_status = "STARTING"
        self.status_changed.emit("STARTING")

    def stop_server(self):
        self.log_output.emit("Stop button clicked.") # Debug log
        self.is_restarting = False
        if self.process.state() != QProcess.NotRunning:
            # If already stopping (user clicked stop again), force kill
            if hasattr(self, 'is_stopping') and self.is_stopping:
                self.log_output.emit("Force killing server...")
                self.log_history.append("Force killing server...")
                self.kill_server(restart=False)
                self.is_stopping = False
                return

            self.is_stopping = True
            self.write_command("stop")
            self.current_status = "STOPPING"
            self.status_changed.emit("STOPPING")
            
    def kill_server(self, restart=False):
        if not restart:
            self.is_restarting = False
        
        if self.process.state() != QProcess.NotRunning:
            self.process.kill()

    def restart_server(self):
        self.is_restarting = True # Always intention to restart
        
        state = self.process.state()
        if state == QProcess.Starting:
            self.log_output.emit("Process is in startup, killing to restart...")
            self.kill_server(restart=True)
            
        elif state == QProcess.Running:
            self.write_command("stop")
            self.current_status = "RESTARTING"
            self.status_changed.emit("RESTARTING")
            self.log_output.emit("Server restart initiated...")
            self.log_history.append("Server restart initiated...")
            
        else: # NotRunning
            self.is_restarting = False # Reset just in case
            self.start_server()

    def write_command(self, cmd):
        if self.process.state() != QProcess.NotRunning:
            data = QByteArray(f"{cmd}\n".encode('utf-8'))
            self.process.write(data)

    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        text = str(data, encoding='utf-8', errors='replace').strip()
        if text:
            self.log_output.emit(text)
            self.log_history.append(text)

    def handle_stderr(self):
        data = self.process.readAllStandardError()
        text = str(data, encoding='utf-8', errors='replace').strip()
        if text:
            self.log_output.emit(f"STDERR: {text}")

    def handle_state_change(self, state):
        if state == QProcess.Running:
            self.current_status = "ONLINE"
            self.status_changed.emit("ONLINE")
        elif state == QProcess.NotRunning:
            self.current_status = "OFFLINE"
            self.status_changed.emit("OFFLINE")

    def handle_finished(self):
        self.log_output.emit("Server process ended.")
        self.current_status = "OFFLINE"
        self.status_changed.emit("OFFLINE")
        
        if self.is_restarting:
            self.log_output.emit("Restarting server now...")
            self.is_restarting = False
            self.start_server()
        else:
            self.finished.emit()
