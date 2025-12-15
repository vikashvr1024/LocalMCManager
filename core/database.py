import json
import os
import time
from core.config_manager import config_manager

class DatabaseManager:
    def __init__(self):
        self.servers_file = "servers.json"
        self._cache = []
        
    def connect(self):
        """
        Loads the servers from the JSON file.
        """
        data_path = config_manager.get_data_path()
        if not data_path:
            raise Exception("Data path not configured.")
            
        self.file_path = os.path.join(data_path, self.servers_file)
        
        if not os.path.exists(self.file_path):
            self._save([])
        else:
            try:
                with open(self.file_path, "r") as f:
                    self._cache = json.load(f)
            except:
                self._cache = []

    def _save(self, data):
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=4)
        self._cache = data

    def get_all_servers(self):
        # Refresh cache?
        self.connect()
        return self._cache

    def get_server(self, server_id):
        self.connect()
        for s in self._cache:
            if s['id'] == server_id:
                return s
        return None

    def add_server(self, name, path, jar_type, version, java_path="java", ram_min="2048M", ram_max="4096M"):
        self.connect()
        
        # Generate ID (Simple auto-increment logic based on max id or timestamp)
        new_id = int(time.time()) 
        if self._cache:
             max_id = max(s['id'] for s in self._cache)
             new_id = max(new_id, max_id + 1)

        new_server = {
            "id": new_id,
            "name": name,
            "path": path,
            "jar_type": jar_type,
            "version": version,
            "java_path": java_path,
            "ram_min": ram_min,
            "ram_max": ram_max,
            "created_at": time.time()
        }
        
        self._cache.append(new_server)
        self._save(self._cache)
        return new_id
        
    def update_server_options(self, server_id, java_path, ram_min, ram_max):
        self.connect()
        for s in self._cache:
            if s['id'] == server_id:
                s['java_path'] = java_path
                s['ram_min'] = ram_min
                s['ram_max'] = ram_max
                self._save(self._cache)
                return True
        return False
        
    def delete_server(self, server_id):
        self.connect()
        self._cache = [s for s in self._cache if s['id'] != server_id]
        self._save(self._cache)

    @property
    def conn(self):
        # Compatibility stub for code trying to access .conn.cursor()
        # This will fail if they try real SQL, but we should fix those call sites.
        raise DeprecationWarning("SQL Connection is removed. Use get_server() or get_all_servers().")
        return None

db_manager = DatabaseManager()

