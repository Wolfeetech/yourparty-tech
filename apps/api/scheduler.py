
import time
import logging
import sys
import subprocess
from pathlib import Path
from apps.api.library_service import LibraryService
from apps.api.sync_playlists import sync_playlists
from apps.api.config_secrets import (
    SMB_SERVER, SMB_SHARE, SMB_USERNAME, SMB_PASSWORD,
    LIBRARY_ROOT_WIN
)

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [SCHEDULER] - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("scheduler.log")
    ]
)
logger = logging.getLogger(__name__)

# Config
INGESTION_INTERVAL = 3600  # 1 Hour
PLAYLIST_SYNC_INTERVAL = 300 # 5 Minutes

def ensure_mount():
    """Checks and mounts the Z: drive if missing."""
    drive_letter = "Z:"
    if not Path(drive_letter).exists():
        logger.info(f"Drive {drive_letter} not found. Mounting...")
        unc_path = f"\\\\{SMB_SERVER}\\{SMB_SHARE}"
        cmd = f'net use {drive_letter} "{unc_path}" /USER:{SMB_USERNAME} "{SMB_PASSWORD}"'
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            logger.info("✅ Drive mounted.")
        else:
            logger.error(f"❌ Mount failed: {res.stderr}")

def run_scheduler():
    logger.info("🚀 Starting YourParty Radio Automation Scheduler")
    
    last_ingestion = 0
    last_playlist_sync = 0
    
    # Initial Drive Check
    ensure_mount()

    while True:
        current_time = time.time()
        
        # 1. Playlist Sync (Frequent)
        if current_time - last_playlist_sync > PLAYLIST_SYNC_INTERVAL:
            logger.info("🔄 Running Playlist Sync...")
            try:
                sync_playlists()
                logger.info("✅ Playlist Sync Complete.")
            except Exception as e:
                logger.error(f"⚠️ Playlist Sync Failed: {e}")
            last_playlist_sync = current_time

        # 2. Ingestion (Hourly)
        if current_time - last_ingestion > INGESTION_INTERVAL:
            logger.info("🎤 Running Library Ingestion...")
            try:
                # Re-verify mount before heavy IO
                ensure_mount()
                
                # Init service
                service = LibraryService(LIBRARY_ROOT_WIN)
                service.run_ingestion()
                
                logger.info("✅ Ingestion Complete.")
            except Exception as e:
                logger.error(f"⚠️ Ingestion Failed: {e}")
            last_ingestion = current_time
            
        # Sleep
        time.sleep(10)

if __name__ == "__main__":
    run_scheduler()
