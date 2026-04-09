import os
import sys
import logging
import time
from pathlib import Path
from typing import Dict, Any

# Fix Path for Imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mongo_client import MongoDatabaseClient
from azuracast_client import AzuraCastClient
from tag_improver import TagImprover
from genre_organizer import GenreOrganizer
from music_scanner import MusicScanner
from config_secrets import (
    MONGO_URI, AZURACAST_API_URL, AZURACAST_API_KEY, AZURACAST_STATION_ID,
    LIBRARY_ROOT_WIN
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("LibraryManager")

import asyncio

class LibraryManager:
    def __init__(self):
        self.mongo = MongoDatabaseClient(MONGO_URI)
        self.azura = AzuraCastClient(AZURACAST_API_URL, AZURACAST_API_KEY, AZURACAST_STATION_ID)
        self.improver = TagImprover()
        self.scanner = MusicScanner()
        
        # Configuration - network share library root
        self.library_dir = LIBRARY_ROOT_WIN
        self.inbox_dir = os.path.join(self.library_dir, "Inbox")
        self.organizer = GenreOrganizer(self.library_dir)

    async def process_inbox(self):
        """Processes all files in the Inbox: Tag -> Organize -> Sync"""
        if not os.path.exists(self.inbox_dir):
            logger.error(f"Inbox not found: {self.inbox_dir}")
            return

        logger.info(f"🚀 Processing Inbox: {self.inbox_dir}")
        files = list(self.scanner.scan_directory(self.inbox_dir))
        
        for file_entry in files:
            path = file_entry['path']
            logger.info(f"--- Processing: {os.path.basename(path)} ---")
            
            # 1. Improve Tags via MusicBrainz
            tag_result = self.improver.improve_tags(path)
            metadata = tag_result['metadata'] if tag_result['success'] else file_entry['metadata']
            
            # 2. Organize into Library FS
            org_result = self.organizer.organize_file(path, metadata)
            if not org_result['success']:
                logger.error(f"Failed to organize {path}: {org_result.get('error')}")
                continue
            
            new_path = org_result['destination']
            rel_path = self.mongo.normalize_path(new_path)
            
            # 3. Update MongoDB
            self.mongo.tracks_collection.update_one(
                {"relative_path": rel_path},
                {"$set": {
                    "file_path": new_path,
                    "relative_path": rel_path,
                    "metadata": metadata,
                    "last_synced": time.time()
                }},
                upsert=True
            )
            logger.info(f"✅ Indexed: {rel_path}")

        # 4. Trigger AzuraCast rescan if files were moved
        if files:
            logger.info("📡 Triggering AzuraCast Media Rescan...")
            await self.azura.rescan_media()

if __name__ == "__main__":
    manager = LibraryManager()
    asyncio.run(manager.process_inbox())
