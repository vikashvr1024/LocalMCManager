import requests
import os
import json

class Downloader:
    def get_versions(self, loader_type):
        loader_type = loader_type.lower()
        if loader_type == "spigot": loader_type = "paper" # Use Paper for Spigot as requested
        
        try:
            if loader_type == "vanilla":
                # Official Mojang Manifest
                return [v["id"] for v in requests.get(
                    "https://launchermeta.mojang.com/mc/game/version_manifest.json"
                ).json()["versions"] if v["type"] == "release"]
            
            elif loader_type == "paper":
                # PaperMC API
                return requests.get(
                    "https://api.papermc.io/v2/projects/paper"
                ).json()["versions"][::-1] # Newest first
            
            elif loader_type == "purpur":
                # Purpur API
                versions = requests.get("https://api.purpurmc.org/v2/purpur").json()["versions"]
                return sorted(versions, key=lambda v: tuple(map(int, v.split("."))), reverse=True)

            elif loader_type == "fabric":
                # Fabric Meta API
                return [
                    v["version"] for v in requests.get(
                        "https://meta.fabricmc.net/v2/versions/game"
                    ).json() if v["stable"]
                ]
            
            elif loader_type == "forge":
                # Forge Promotions
                data = requests.get("https://files.minecraftforge.net/net/minecraftforge/forge/promotions_slim.json").json().get("promos", {})
                versions = {
                    k.split("-")[0] for k in data.keys() if k[0].isdigit()
                }
                return sorted(list(versions), key=lambda v: tuple(map(int, v.split('.'))), reverse=True)

            # Fallback
            return ["1.21.4", "1.21.3", "1.21.1", "1.21", "1.20.4", "1.20.2", "1.20.1"]
            
        except Exception as e:
            print(f"Error fetching versions for {loader_type}: {e}")
            return ["1.20.4", "1.20.2", "1.20.1"] # Fallback

    def get_download_url(self, loader_type, version):
        loader_type = loader_type.lower()
        if loader_type == "spigot": loader_type = "paper"
        
        try:
            if loader_type == "vanilla":
                # Official Mojang Manifest
                r = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json")
                versions = r.json()["versions"]
                target_url = next((v["url"] for v in versions if v["id"] == version), None)
                if target_url:
                    r2 = requests.get(target_url)
                    return r2.json()["downloads"]["server"]["url"]
            
            elif loader_type == "paper":
                # PaperMC API
                r = requests.get(f"https://api.papermc.io/v2/projects/paper/versions/{version}")
                builds = r.json().get("builds", [])
                if not builds: return None
                latest_build = builds[-1]
                return f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{latest_build}/downloads/paper-{version}-{latest_build}.jar"
            
            elif loader_type == "purpur":
                # Purpur API
                r = requests.get(f"https://api.purpurmc.org/v2/purpur/{version}")
                data = r.json()
                
                # Check inside 'builds' for 'all' list
                builds_data = data.get("builds", {})
                all_builds = builds_data.get("all", [])
                
                if not all_builds: 
                    # Fallback if 'all' list is missing, filter digit keys from builds dict
                    keys = [k for k in builds_data.keys() if k.isdigit()]
                    all_builds = sorted(keys, key=int)
                
                if not all_builds: return None
                latest_build = all_builds[-1]
                return f"https://api.purpurmc.org/v2/purpur/{version}/{latest_build}/download"

            elif loader_type == "fabric":
                # Fabric Meta API
                # Get Loader
                r = requests.get("https://meta.fabricmc.net/v2/versions/loader")
                # Assuming first is stable/newest
                loaders = r.json()
                loader_ver = next((l["version"] for l in loaders if l["stable"]), loaders[0]["version"])
                
                # Get Installer
                r2 = requests.get("https://meta.fabricmc.net/v2/versions/installer")
                installers = r2.json()
                installer_ver = next((i["version"] for i in installers if i["stable"]), installers[0]["version"])
                
                return f"https://meta.fabricmc.net/v2/versions/loader/{version}/{loader_ver}/{installer_ver}/server/jar"

            elif loader_type == "forge":
                # Forge Promotions
                r = requests.get("https://files.minecraftforge.net/net/minecraftforge/forge/promotions_slim.json")
                promos = r.json().get("promos", {})
                
                forge_ver = promos.get(f"{version}-recommended")
                if not forge_ver:
                    forge_ver = promos.get(f"{version}-latest")
                    
                if not forge_ver:
                    return None
                 
                return f"https://maven.minecraftforge.net/net/minecraftforge/forge/{version}-{forge_ver}/forge-{version}-{forge_ver}-installer.jar"

        except Exception as e:
            print(f"Error getting URL for {loader_type} {version}: {e}")
        return None

    def download_jar(self, url, save_path, progress_callback=None):
        if not url: return False
        try:
            # Create parent dir
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            headers = {'User-Agent': 'LocalMCManager/1.0'}
            r = requests.get(url, stream=True, headers=headers)
            r.raise_for_status()
            
            total_len = int(r.headers.get('content-length', 0))
            downloaded = 0
            
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_len > 0:
                            percent = int((downloaded / total_len) * 100)
                            progress_callback(percent)
            return True
        except Exception as e:
            print(f"Download Error: {e}")
            return False

downloader = Downloader()

