# Local MC Manager

A modern, lightweight, and powerful local Minecraft server manager built with Python and PySide6.

## 🚀 Features

*   **Server Management**: Create, start, stop, and manage multiple Minecraft servers effortlessly.
*   **Version Control**: Automatically fetch and install the latest versions of various server types:
    *   Vanilla
    *   Paper
    *   Purpur
    *   Fabric
    *   Forge
    *   Spigot
*   **Performance Monitoring**: Real-time RAM and CPU usage tracking for each server.
*   **Configuration**: Easy-to-use GUI for adjusting server properties (`server.properties`), RAM allocation, and Java version.
*   **Console Access**: direct access to the server console for executing commands.
*   **Modern UI**: Sleek, dark-themed interface designed for usability.
*   **Standalone**: No external dependencies required (bundled with PyInstaller).

## 🛠️ Installation

### Windows Installer (Recommended)
1.  Download the latest `LocalMCManagerSetup.exe` from the [Releases](https://github.com/vikashvr1024/LocalMCManager/releases) page.
2.  Run the installer and follow the on-screen instructions.
3.  Launch "Local MC Manager" from your desktop or Start Menu.

### Manual Installation (Portable)
1.  Download `LocalMCManager.exe` from the Releases page.
2.  Place it in a folder of your choice (e.g., `C:\Games\MCManager`).
3.  Run the executable.

### Running from Source
1.  Ensure you have Python 3.10+ installed.
2.  Clone the repository:
    ```bash
    git clone https://github.com/vikashvr1024/LocalMCManager.git
    cd LocalMCManager
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Run the application:
    ```bash
    python main.py
    ```

## 📦 Building from Source

To build the executable yourself:

1.  Install the requirements.
2.  Run the build script:
    ```bash
    python build_exe.py
    ```
3.  The standalone EXE will be in the `dist` folder.

To build the installer (requires **Inno Setup**):
1.  Build the EXE first.
2.  Open `setup.iss` with Inno Setup Compiler.
3.  Compile the script.

## 📝 Usage

1.  **Create a Server**: Click the "+" button, enter a name, select a version/type, and click "Create".
2.  **Start Server**: Select a server from the list and click "Start".
3.  **Manage**: Click "Dashboard" to view stats, "Console" to run commands, or "Options" to configure settings.

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## 👤 Author

**Vikash**
*   GitHub: [@vikashvr1024](https://github.com/vikashvr1024)
