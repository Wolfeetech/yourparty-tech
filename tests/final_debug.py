#!/usr/bin/env python3
import sys
import os
import asyncio
import logging
import inspect
from dotenv import load_dotenv

sys.path.insert(0, '/opt/radio-api')
load_dotenv('/opt/radio-api/.env')

logging.basicConfig(level=logging.INFO, stream=sys.stdout, force=True)
logger = logging.getLogger(__name__)

from mongo_client import MongoDatabaseClient
from config_secrets import MONGO_URI

async def test():
    logger.info("=== DEBUGGING MONGO DB ===")
    mc = MongoDatabaseClient(MONGO_URI)
    
    # 1. Print Source Code
    logger.info("--- Source of get_tracks_for_playlist ---")
    src = inspect.getsource(mc.get_tracks_for_playlist)
    print(src)
    logger.info("-----------------------------------------")

    # 2. Direct Query Check
    logger.info(f"Checking access to collection: {mc.tracks_collection.name}")
    count = mc.tracks_collection.count_documents({})
    logger.info(f"Total Tracks: {count}")
    
    mood_count = mc.tracks_collection.count_documents({"mood": "Euphoric"})
    logger.info(f"Tracks with mood='Euphoric': {mood_count}")
    
    # 3. Check AzuraCast ID
    ac_count = mc.tracks_collection.count_documents({"azuracast_id": {"$exists": True}})
    logger.info(f"Tracks with azuracast_id: {ac_count}")
    
    # 4. Check Junction
    junction = mc.tracks_collection.count_documents({
        "mood": "Euphoric",
        "azuracast_id": {"$exists": True, "$ne": None}
    })
    logger.info(f"Tracks with mood='Euphoric' AND azuracast_id: {junction}")

    # 5. Run the function
    try:
        ids = mc.get_tracks_for_playlist("Euphoric")
        logger.info(f"Function returned {len(ids)} IDs")
    except Exception as e:
        logger.error(f"Function CRASHED: {e}")

if __name__ == "__main__":
    asyncio.run(test())
