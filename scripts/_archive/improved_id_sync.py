#!/usr/bin/env python3
"""
Improved ID Sync Script
=======================
Matches AzuraCast media to MongoDB tracks using multiple strategies:
1. song_id match (hash-based)
2. Relative path match (normalized)
3. Filename match (fallback)
"""
import os
import sys
import asyncio
import logging
from pymongo import UpdateOne

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(PROJECT_ROOT, "apps", "api"))

from mongo_client import MongoDatabaseClient
from azuracast_client import AzuraCastClient
from config_secrets import MONGO_URI, AZURACAST_API_URL, AZURACAST_API_KEY, AZURACAST_STATION_ID

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("IDSync")

class ImprovedIDSync:
    def __init__(self):
        self.mongo = MongoDatabaseClient(MONGO_URI)
        self.azura = AzuraCastClient(AZURACAST_API_URL, AZURACAST_API_KEY, AZURACAST_STATION_ID)
    
    def normalize_to_relative(self, full_path: str) -> str:
        """Convert any absolute path to a comparable relative path."""
        normalized = full_path.replace("\\", "/").strip("/")
        
        # Strip known prefixes
        prefixes = [
            "z:/radio_library/",
            "m:/library/",
            "/var/azuracast/stations/yourparty/media/"
        ]
        
        lower = normalized.lower()
        for prefix in prefixes:
            if lower.startswith(prefix):
                return normalized[len(prefix):]
        
        return normalized
    
    async def run_sync(self):
        logger.info("🔗 Starting Improved ID Sync...")
        
        # 1. Build a lookup from MongoDB
        logger.info("Step 1: Building MongoDB index...")
        mongo_tracks = list(self.mongo.tracks_collection.find())
        
        # Create multiple lookup dictionaries
        by_song_id = {}
        by_rel_path = {}
        by_filename = {}
        
        for track in mongo_tracks:
            tid = track.get('_id')
            song_id = track.get('song_id')
            file_path = track.get('file_path', '')
            
            if song_id:
                by_song_id[song_id] = tid
            
            rel_path = self.normalize_to_relative(file_path)
            by_rel_path[rel_path.lower()] = tid
            
            filename = rel_path.split("/")[-1].lower()
            if filename not in by_filename:
                by_filename[filename] = []
            by_filename[filename].append(tid)
        
        logger.info(f"Indexed {len(mongo_tracks)} tracks ({len(by_song_id)} with song_id)")
        
        # 2. Fetch AzuraCast media
        logger.info("Step 2: Fetching AzuraCast media...")
        az_media = await self.azura.get_station_media()
        logger.info(f"Retrieved {len(az_media)} tracks from AzuraCast")
        
        # 3. Match and update
        logger.info("Step 3: Matching and updating...")
        updates = []
        matched = 0
        match_by_filename = 0
        match_by_path = 0
        match_by_songid = 0
        
        for media in az_media:
            az_id = media.get('id')
            az_song_id = media.get('song_id')
            az_path = media.get('path', '')
            az_filename = az_path.split("/")[-1].lower() if az_path else ''
            az_rel = self.normalize_to_relative(az_path).lower()
            
            mongo_id = None
            
            # Strategy 1: filename match (most reliable for this case)
            if az_filename in by_filename:
                candidates = by_filename[az_filename]
                if len(candidates) == 1:
                    mongo_id = candidates[0]
                    match_by_filename += 1
            
            # Strategy 2: relative path match
            if not mongo_id and az_rel in by_rel_path:
                mongo_id = by_rel_path[az_rel]
                match_by_path += 1
            
            # Strategy 3: song_id match (unlikely to work for this DB)
            if not mongo_id and az_song_id and az_song_id in by_song_id:
                mongo_id = by_song_id[az_song_id]
                match_by_songid += 1
            
            if mongo_id:
                updates.append(UpdateOne(
                    {"_id": mongo_id},
                    {"$set": {"azuracast_id": az_id, "azuracast_path": az_path}}
                ))
                matched += 1
        
        logger.info(f"Match breakdown: filename={match_by_filename}, path={match_by_path}, song_id={match_by_songid}")
        
        # 4. Execute updates
        if updates:
            result = self.mongo.tracks_collection.bulk_write(updates)
            logger.info(f"✅ Updated {result.modified_count} records (Matched: {matched})")
        else:
            logger.warning("No matches found!")
        
        return matched

if __name__ == "__main__":
    sync = ImprovedIDSync()
    asyncio.run(sync.run_sync())
