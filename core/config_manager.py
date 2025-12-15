import os
import sys
import configparser
from pathlib import Path

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

CONFIG_FILE = "config.ini"

class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance.config = configparser.ConfigParser()
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        if os.path.exists(CONFIG_FILE):
            self.config.read(CONFIG_FILE)

    def is_configured(self):
        return "GENERAL" in self.config and "data_path" in self.config["GENERAL"]

    def get_data_path(self):
        if self.is_configured():
            return Path(self.config["GENERAL"]["data_path"])
        return None

    def set_data_path(self, path):
        if "GENERAL" not in self.config:
            self.config["GENERAL"] = {}
        self.config["GENERAL"]["data_path"] = str(path)
        with open(CONFIG_FILE, "w") as f:
            self.config.write(f)
        
        # Ensure directory exists
        os.makedirs(path, exist_ok=True)

    def get_db_path(self):
        # Deprecated but kept for compatibility logic if needed
        return None

config_manager = ConfigManager()
