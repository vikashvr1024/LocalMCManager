from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeView, 
                               QFileSystemModel, QPushButton, QMenu, QMessageBox, QInputDialog,
                               QDialog, QTextEdit, QFileDialog)
from PySide6.QtCore import QDir, Qt, Signal
from PySide6.QtGui import QAction, QDesktopServices, QCursor
from PySide6.QtCore import QUrl
import shutil
import os

class TextEditorDialog(QDialog):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.setWindowTitle(f"Edit - {os.path.basename(file_path)}")
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        self.editor = QTextEdit()
        self.editor.setStyleSheet("background-color: #1E1E1E; color: #D4D4D4; font-family: Consolas, monospace; font-size: 14px;")
        
        # Load content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.editor.setText(f.read())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not read file: {e}")
            self.editor.setReadOnly(True)
            
        layout.addWidget(self.editor)
        
        # Buttons
        btns = QHBoxLayout()
        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self.save)
        self.btn_save.setStyleSheet("background-color: #007ACC; color: white; padding: 5px 15px;")
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        
        btns.addStretch()
        btns.addWidget(self.btn_save)
        btns.addWidget(self.btn_cancel)
        layout.addLayout(btns)
        
    def save(self):
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            self.accept()
        except Exception as e:
             QMessageBox.critical(self, "Error", f"Could not save file: {e}")

class FileManager(QWidget):
    def __init__(self, server_path):
        super().__init__()
        self.server_path = server_path
        
        layout = QVBoxLayout(self)
        
        # Tools
        tools = QHBoxLayout()
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.clicked.connect(self.refresh)
        
        self.btn_upload = QPushButton("Upload File")
        self.btn_upload.setStyleSheet("background-color: #4CAF50; color: white;")
        self.btn_upload.clicked.connect(self.upload_file)
        
        self.btn_open_folder = QPushButton("Open in Explorer")
        self.btn_open_folder.clicked.connect(self.open_system_folder)
        
        tools.addWidget(self.btn_refresh)
        tools.addWidget(self.btn_upload)
        tools.addWidget(self.btn_open_folder)
        tools.addStretch()
        layout.addLayout(tools)
        
        # Tree View
        self.model = QFileSystemModel()
        self.model.setRootPath(server_path)
        self.model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)
        
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(server_path))
        self.tree.setAnimated(True)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.open_context_menu)
        
        # Adjust column sizes
        self.tree.header().resizeSection(0, 300) # Name
        self.tree.header().resizeSection(1, 80)  # Size
        self.tree.header().resizeSection(2, 100) # Type
        
        # Style
        self.tree.setStyleSheet("""
            QTreeView {
                background-color: #252526;
                color: #CCCCCC;
                border: 1px solid #3E3E42;
            }
            QHeaderView::section {
                background-color: #333;
                color: white;
                border: none;
                padding: 4px;
            }
        """)
        
        layout.addWidget(self.tree)

    def refresh(self):
        # QFileSystemModel auto-watches, but sometimes force needed
        pass

    def open_system_folder(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.server_path))
        
    def upload_file(self):
        # Determine current directory from selection or default to root
        target_dir = self.server_path
        indexes = self.tree.selectedIndexes()
        if indexes:
             path = self.model.filePath(indexes[0])
             if os.path.isdir(path):
                 target_dir = path
             else:
                 target_dir = os.path.dirname(path)
                 
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Upload")
        if file_path:
            filename = os.path.basename(file_path)
            dest = os.path.join(target_dir, filename)
            try:
                shutil.copy2(file_path, dest)
                QMessageBox.information(self, "Success", f"Uploaded {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to upload: {e}")

    def open_context_menu(self, position):
        indexes = self.tree.selectedIndexes()
        if not indexes:
            return
            
        index = indexes[0]
        file_path = self.model.filePath(index)
        
        menu = QMenu()
        
        # Edit option for text files
        if not os.path.isdir(file_path):
             menu.addAction("Edit").triggered.connect(lambda: self.edit_file(file_path))
        
        open_action = QAction("Open (System)", self)
        rename_action = QAction("Rename", self)
        delete_action = QAction("Delete", self)
        
        open_action.triggered.connect(lambda: self.open_file(file_path))
        rename_action.triggered.connect(lambda: self.rename_file(index, file_path))
        delete_action.triggered.connect(lambda: self.delete_file(file_path))
        
        menu.addSeparator()
        menu.addAction(open_action)
        menu.addAction(rename_action)
        menu.addSeparator()
        menu.addAction(delete_action)
        
        menu.exec(QCursor.pos())

    def edit_file(self, path):
        # Check size limit or binary? For now try-catch in dialog handles it
        dlg = TextEditorDialog(path, self)
        dlg.exec()

    def open_file(self, path):
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def rename_file(self, index, path):
        name = self.model.fileName(index)
        new_name, ok = QInputDialog.getText(self, "Rename", "New Name:", text=name)
        if ok and new_name:
            dir_path = os.path.dirname(path)
            new_path = os.path.join(dir_path, new_name)
            try:
                os.rename(path, new_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def delete_file(self, path):
        ret = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete {os.path.basename(path)}?",
                                   QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
