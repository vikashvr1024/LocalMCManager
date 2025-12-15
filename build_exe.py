import PyInstaller.__main__
import os
import shutil

# Clean previous builds
for folder in ["dist", "build", "__pycache__"]:
    if os.path.exists(folder):
        shutil.rmtree(folder)

print("Building Local MC Manager with PyInstaller...")

PyInstaller.__main__.run([
    'main.py',
    '--name=LocalMCManager',
    '--onefile',                  # Single EXE (remove if you prefer folder)
    '--windowed',                 # No console window
    '--clean',
    '--icon=assets/icon.ico',
    # Data folders
    '--add-data=assets;assets',
    '--add-data=core;core',
    '--add-data=gui;gui',
    # Hidden imports for PySide6/Qt
    '--hidden-import=PySide6.QtXml',
    '--hidden-import=shiboken6',
    # Optional: Reduce size / improve startup
    '--exclude-module=tkinter',
    '--exclude-module=matplotlib',
])

print("Build complete! EXE is in 'dist/LocalMCManager.exe'")
print("Test it thoroughly before sharing.")
