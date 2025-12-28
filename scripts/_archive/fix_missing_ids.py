import os
import sys
import logging
import re
from pymongo import UpdateOne

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(PROJECT_ROOT, "apps", "api"))

from mongo_client import MongoDatabaseClient
from azuracast_client import AzuraCastClient
from config_secrets import MONGO_URI, AZURACAST_API_URL, AZURACAST_API_KEY, AZURACAST_STATION_ID

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("IDFixer")

import asyncio

class IDFixer:
    def __init__(self, dry_run=True):
        self.mongo = MongoDatabaseClient(MONGO_URI)
        self.azura = AzuraCastClient(AZURACAST_API_URL, AZURACAST_API_KEY, AZURACAST_STATION_ID)
        self.dry_run = dry_run
        if dry_run:
            logger.info("🧪 DRY RUN MODE ENABLED - No changes will be written to DB.")

    async def run_repair(self):
        """
        1. Normalizes all paths to relative_path.
        2. Fetches all media from AzuraCast.
        3. Matches and backfills azuracast_id.
        """
        logger.info("🛠 Starting Database Repair & ID Backfill...")
        
        # 1. Normalisierung der Pfade
        logger.info("Step 1: Normalizing paths...")
        tracks = list(self.mongo.tracks_collection.find())
        bulk_ops = []
        for track in tracks:
            full_path = track.get('file_path')
            if full_path:
                rel_path = self.mongo.normalize_path(full_path)
                if rel_path != track.get('relative_path'):
                    bulk_ops.append(UpdateOne(
                        {"_id": track["_id"]},
                        {"$set": {"relative_path": rel_path}}
                    ))
        
        if bulk_ops:
            if not self.dry_run:
                res = self.mongo.tracks_collection.bulk_write(bulk_ops)
                logger.info(f"Normalized {res.modified_count} records.")
            else:
                logger.info(f"[DRY RUN] Would normalize {len(bulk_ops)} records.")

        # 2. AzuraCast Media abrufen (ASYNC)
        logger.info("Step 2: Fetching live media from AzuraCast...")
        try:
            az_media = await self.azura.get_station_media()
            logger.info(f"Retrieved {len(az_media)} tracks from AzuraCast.")
        except Exception as e:
            logger.error(f"Failed to fetch AzuraCast media: {e}")
            return

        # 3. IDs abgleichen
        logger.info("Step 3: Matching and backfilling IDs...")
        id_ops = []
        matched_count = 0
        
        for media in az_media:
            az_id = media.get('id')
            az_rel_path = media.get('path')
            
            if not az_id or not az_rel_path:
                continue
                
            clean_rel_path = az_rel_path.replace("\\", "/").strip("/")
            
            id_ops.append(UpdateOne(
                {"$or": [
                    {"relative_path": clean_rel_path},
                    {"file_path": {"$regex": re.escape(clean_rel_path) + "$", "$options": "i"}}
                ]},
                {"$set": {"azuracast_id": az_id, "azuracast_path": az_rel_path}}
            ))
        
        if id_ops:
            if not self.dry_run:
                chunk_size = 500
                for i in range(0, len(id_ops), chunk_size):
                    chunk = id_ops[i:i + chunk_size]
                    res = self.mongo.tracks_collection.bulk_write(chunk)
                    matched_count += res.modified_count
            else:
                logger.info(f"[DRY RUN] Would update/backfill {len(id_ops)} potential matches.")
        
        logger.info(f"✅ Repair Complete! Total Matches/Updated: {matched_count}")

if __name__ == "__main__":
    fixer = IDFixer(dry_run=False)
    asyncio.run(fixer.run_repair())
