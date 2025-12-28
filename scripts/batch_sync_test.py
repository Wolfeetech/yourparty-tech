#!/usr/bin/env python3
"""Small batch sync test - just 10 tracks to verify matching works."""
import os
import sys
import asyncio
import logging

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(PROJECT_ROOT, "apps", "api"))

from mongo_client import MongoDatabaseClient
from azuracast_client import AzuraCastClient
from config_secrets import MONGO_URI, AZURACAST_API_URL, AZURACAST_API_KEY, AZURACAST_STATION_ID

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BatchTest")

async def test_batch():
    mongo = MongoDatabaseClient(MONGO_URI)
    azura = AzuraCastClient(AZURACAST_API_URL, AZURACAST_API_KEY, AZURACAST_STATION_ID)
    
    # Build filename index
    filename_to_id = {}
    for doc in mongo.tracks_collection.find():
        fp = doc.get('file_path', '')
        if fp:
            fn = fp.replace("\\", "/").split("/")[-1].lower()
            if fn not in filename_to_id:
                filename_to_id[fn] = doc['_id']
    
    logger.info(f"Indexed {len(filename_to_id)} unique filenames")
    
    # Fetch AzuraCast and test first 10
    az_media = await azura.get_station_media()
    logger.info(f"Got {len(az_media)} tracks from AzuraCast")
    
    matched = 0
    updated = 0
    
    for i, media in enumerate(az_media[:20]):  # Just first 20
        az_id = media.get('id')
        az_path = media.get('path', '')
        az_fn = az_path.split("/")[-1].lower() if az_path else ''
        
        logger.debug(f"AzuraCast filename: {az_fn}")
        
        if az_fn in filename_to_id:
            matched += 1
            mongo_id = filename_to_id[az_fn]
            
            result = mongo.tracks_collection.update_one(
                {"_id": mongo_id},
                {"$set": {"azuracast_id": az_id, "azuracast_path": az_path}}
            )
            
            if result.modified_count > 0:
                updated += 1
                logger.info(f"✅ Updated: {az_fn} -> azuracast_id={az_id}")
            else:
                logger.warning(f"⚠️ Matched but not modified: {az_fn}")
        else:
            logger.debug(f"❌ No match for: {az_fn}")
    
    logger.info(f"Results: Matched={matched}, Updated={updated}")
    
    # Verify count
    count = mongo.tracks_collection.count_documents({'azuracast_id': {'$exists': True}})
    logger.info(f"Total tracks with azuracast_id: {count}")

if __name__ == "__main__":
    asyncio.run(test_batch())
