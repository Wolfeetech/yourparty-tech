import asyncio
import os
import logging
from dotenv import load_dotenv
import sys

# Ensure we can import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mongo_client import MongoDatabaseClient
try:
    from music_scanner import MusicScanner
except ImportError:
    from apps.api.music_scanner import MusicScanner

# Try to recover secrets
try:
    from config_secrets import SMB_SERVER, SMB_SHARE, SMB_USERNAME, SMB_PASSWORD
    SECRETS_FOUND = True
except ImportError:
    SECRETS_FOUND = False
    SMB_SERVER = SMB_SHARE = SMB_USERNAME = SMB_PASSWORD = None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ManualSync")

def main():
    logger.info("Loading environment...")
    load_dotenv()
    
    if SECRETS_FOUND:
        print(f"\n!!! SECRETS RECOVERED !!!")
        print(f"SMB_SERVER: {SMB_SERVER}")
        print(f"SMB_SHARE: {SMB_SHARE}")
        print(f"SMB_USERNAME: {SMB_USERNAME}")
        print(f"SMB_PASSWORD: {SMB_PASSWORD}")
        print(f"!!! END SECRETS !!!\n")
    else:
        logger.warning("Could not import config_secrets.")

    # 1. Connect to Mongo
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        mongo_uri = "mongodb://192.168.178.222:27017/" 
        
    logger.info(f"Connecting to Mongo: {mongo_uri}")
    mongo = MongoDatabaseClient(mongo_uri, "yourparty")
    
    # 2. Init Scanner
    scanner = MusicScanner()
    
    # 3. Sync
    library_root = (
        os.getenv("LIBRARY_ROOT_LINUX")
        or os.getenv("MUSIC_DIR")
        or "/var/radio/music/yourparty_Libary"
    )
    if not os.path.exists(library_root):
        logger.error(f"Directory {library_root} not found!")
        return

    logger.info(f"Scanning {library_root}...")
    
    # Synchronous iteration of generator
    count = 0
    synced = 0
    
    try:
        for file_entry in scanner.scan_directory(library_root):
            count += 1
            mongo.sync_track_metadata(file_entry['path'], file_entry['metadata'])
            synced += 1
            if count % 100 == 0:
                 logger.info(f"Synced {synced} tracks...")
    except Exception as e:
        logger.error(f"Scan Loop Error: {e}")
        
    logger.info(f"Successfully synced {synced} tracks total.")

if __name__ == "__main__":
    main()
