
import os
import logging
import sys
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load environment early so path config uses .env values.
load_dotenv()

# Ensure we can import app modules. 
# Assuming script is deployed to /app/scripts/ and app root is /app/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Also try adding /app explicitly if running on container
if "/app" not in sys.path:
    sys.path.append("/app")

try:
    # Direct imports for flat structure in /app
    from genre_organizer import GenreOrganizer
    from music_scanner import MusicScanner
    from mongo_client import MongoDatabaseClient
except ImportError as e:
    print(f"Import Error: {e}")
    # Fallback to relative if needed?
    from apps.api.music_scanner import MusicScanner
    from apps.api.mongo_client import MongoDatabaseClient

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [LibraryAuto] - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("/var/log/radio_library_auto.log")
    ]
)
logger = logging.getLogger("LibraryAuto")

# Configuration (Server Paths)
LIBRARY_ROOT_LINUX = (
    os.getenv("LIBRARY_ROOT_LINUX")
    or os.getenv("MUSIC_DIR")
    or "/var/radio/music/yourparty_Libary"
)
INBOX_DIR = os.path.join(LIBRARY_ROOT_LINUX, "Inbox")
LIBRARY_DIR = os.path.join(LIBRARY_ROOT_LINUX, "Library")
ARCHIVE_DIR = os.path.join(LIBRARY_ROOT_LINUX, "Archive")

def ensure_dirs():
    for d in [INBOX_DIR, LIBRARY_DIR, ARCHIVE_DIR]:
        if not os.path.exists(d):
            os.makedirs(d)
            logger.info(f"Created directory: {d}")

def sync_to_mongo(file_path, metadata):
    """Update MongoDB with new track info."""
    try:
        mongo_uri = os.getenv("MONGO_URI", "mongodb://192.168.178.222:27017/")
        mongo = MongoDatabaseClient(mongo_uri, "yourparty")
        mongo.sync_track_metadata(file_path, metadata)
        # mongo.close() # Client might not have close, keep it simple
    except Exception as e:
        logger.error(f"Mongo Sync Failed: {e}")

def run_automation():
    load_dotenv()
    logger.info("Starting Library Automation Run...")
    ensure_dirs()
    
    organizer = GenreOrganizer(LIBRARY_DIR)
    scanner = MusicScanner()
    
    # 1. Scan Inbox
    files_found = 0
    files_moved = 0
    
    # We list first to avoid modifying while iterating if possible, 
    # though scanner generator is usually fine.
    # But detailed organize logic moves file, so simpler to just process one by one.
    
    try:
        for file_entry in scanner.scan_directory(INBOX_DIR):
            files_found += 1
            file_path = file_entry['path']
            metadata = file_entry['metadata']
            
            logger.info(f"Processing Incoming: {os.path.basename(file_path)}")
            
            # Organize (Move to Library)
            result = organizer.organize_file(
                file_path, 
                metadata, 
                dry_run=False, 
                output_path=LIBRARY_DIR
            )
            
            if result['success']:
                files_moved += 1
                new_path = result.get('destination')
                if new_path:
                    # Sync Result to DB immediately
                    logger.info(f"Syncing to DB: {new_path}")
                    sync_to_mongo(new_path, metadata)
            else:
                logger.error(f"Failed to organize {file_path}: {result.get('error')}")
                
    except Exception as e:
        logger.error(f"Inbox Scan Error: {e}")

    # 2. Sync Library Scope (Optional: Full verify or just rely on inbox trigger?)
    # For now, Inbox trigger is "Active Implementation".
    
    if files_found == 0:
        logger.info("Inbox empty. Nothing to do.")
    else:
        logger.info(f"Run Complete. Found {files_found}, Organized {files_moved}.")

if __name__ == "__main__":
    run_automation()
