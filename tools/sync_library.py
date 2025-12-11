import os
import sys
import logging
from pymongo import MongoClient
import requests

# Add backend to path to reuse clients if needed, but we'll keep it self-contained for portability
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Load Env
from dotenv import load_dotenv
import pathlib
env_path = pathlib.Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Config from Env
MONGO_URI = os.getenv("MONGO_URI")
AZURACAST_URL = os.getenv("AZURACAST_URL", "http://192.168.178.210")
AZURACAST_KEY = os.getenv("AZURACAST_API_KEY", "9199dc63da6223190:c9f8c3a22e25932753dd3f4d57fa0d9c")
STATION_ID = 1

LOCAL_DRIVE = "M:\\"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SyncManager")

def get_mongo_client():
    try:
        if MONGO_URI:
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        else:
             # Fallback
             client = MongoClient("mongodb://root:yourparty@192.168.178.222:27017/?authSource=admin")
             
        client.server_info() # Trigger connect
        return client
    except Exception as e:
        logger.error(f"Could not connect to MongoDB: {e}")
        return None

def fetch_azuracast_media():
    headers = {
        "Authorization": f"Bearer {AZURACAST_KEY}",
        "Content-Type": "application/json"
    }
    url = f"{AZURACAST_URL}/api/station/{STATION_ID}/files"
    try:
        resp = requests.get(url, headers=headers, timeout=10, verify=False)
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"Failed to fetch from AzuraCast: {e}")
        return []

def scan_local_drive(root_path):
    local_files = {} # relative_path -> full_path
    if not os.path.exists(root_path):
        logger.error(f"Drive {root_path} not found! Please run mount_music.ps1 first.")
        return {}
        
    logger.info(f"Scanning local files in {root_path}...")
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file.lower().endswith(('.mp3', '.flac', '.wav', '.m4a')):
                full_path = os.path.join(root, file)
                # Rel path for matching with AzuraCast (which uses / style)
                rel_path = os.path.relpath(full_path, root_path).replace("\\", "/")
                local_files[rel_path] = full_path
    return local_files

def run_sync():
    logger.info("--- Starting Library Sync ---")
    
    # 1. Connect DB
    mongo = get_mongo_client()
    if not mongo:
        return
    db = mongo['radio_station'] # Assuming db name
    
    # 2. Get AzuraCast Data
    ac_media = fetch_azuracast_media()
    if not ac_media:
        logger.warning("No media found in AzuraCast or API error.")
    
    # 3. Check Local Drive
    local_files = scan_local_drive(LOCAL_DRIVE)
    if not local_files:
        logger.warning("Skipping local file check.")
    
    updated = 0
    
    # 4. Sync Logic
    # We map AzuraCast Unique IDs to our DB entries
    for item in ac_media:
        unique_id = item.get('unique_id')
        path = item.get('path')
        
        if not unique_id: continue
        
        # Check if we have this file locally
        local_path = local_files.get(path)
        exists_locally = local_path is not None
        
        update_data = {
            "metadata": {
                "title": item.get('title'),
                "artist": item.get('artist'),
                "album": item.get('album')
            },
            "azuracast_path": path,
            "on_disk": exists_locally
        }
        
        if exists_locally:
            update_data["local_windows_path"] = local_path
            
        # Update DB
        db.tracks.update_one(
            {"song_id": unique_id},
            {"$set": update_data},
            upsert=True
        )
        updated += 1
        
    logger.info(f"Synced {updated} tracks to MongoDB.")
    
    if updated > 0:
        logger.info("Your database is now in sync with AzuraCast.")

if __name__ == "__main__":
    run_sync()
