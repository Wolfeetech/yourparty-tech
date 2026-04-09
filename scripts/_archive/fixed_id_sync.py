#!/usr/bin/env python3
"""
Fixed ID Sync - Uses direct updates instead of bulk_write
Proven to work based on debug testing.
"""
import os
import sys
import asyncio
import logging

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(PROJECT_ROOT, "apps", "api"))

from mongo_client import MongoDatabaseClient
from azuracast_client import AzuraCastClient
from config_secrets import MONGO_URI, AZURACAST_API_URL, AZURACAST_API_KEY, AZURACAST_STATION_ID

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("IDSyncFixed")

class FixedIDSync:
    def __init__(self):
        self.mongo = MongoDatabaseClient(MONGO_URI)
        self.azura = AzuraCastClient(AZURACAST_API_URL, AZURACAST_API_KEY, AZURACAST_STATION_ID)
    
    async def run_sync(self):
        logger.info("🔗 Starting Fixed ID Sync...")
        
        # 1. Build filename -> _id lookup from MongoDB
        logger.info("Step 1: Building filename index from MongoDB...")
        filename_to_doc = {}
        
        for doc in self.mongo.tracks_collection.find():
            fp = doc.get('file_path', '')
            if fp:
                # Extract filename
                fn = fp.replace("\\", "/").split("/")[-1].lower()
                if fn not in filename_to_doc:
                    filename_to_doc[fn] = doc['_id']
        
        logger.info(f"Indexed {len(filename_to_doc)} unique filenames")
        
        # 2. Fetch AzuraCast media
        logger.info("Step 2: Fetching AzuraCast media...")
        az_media = await self.azura.get_station_media()
        logger.info(f"Retrieved {len(az_media)} tracks from AzuraCast")
        
        # 3. Match and update one by one (proven to work)
        logger.info("Step 3: Matching and updating...")
        matched = 0
        updated = 0
        
        for media in az_media:
            az_id = media.get('id')
            az_path = media.get('path', '')
            
            if not az_id or not az_path:
                continue
            
            az_filename = az_path.split("/")[-1].lower()
            
            if az_filename in filename_to_doc:
                mongo_id = filename_to_doc[az_filename]
                matched += 1
                
                # Direct update (proven to work)
                result = self.mongo.tracks_collection.update_one(
                    {"_id": mongo_id},
                    {"$set": {"azuracast_id": az_id, "azuracast_path": az_path}}
                )
                
                if result.modified_count > 0:
                    updated += 1
        
        logger.info(f"✅ Sync Complete! Matched: {matched}, Updated: {updated}")
        return updated

if __name__ == "__main__":
    sync = FixedIDSync()
    asyncio.run(sync.run_sync())
