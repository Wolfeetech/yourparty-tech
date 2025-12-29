#!/usr/bin/env python3
import sys
import os
import asyncio
import logging
from dotenv import load_dotenv

sys.path.insert(0, '/opt/radio-api')
load_dotenv('/opt/radio-api/.env')

logging.basicConfig(level=logging.INFO, stream=sys.stdout, force=True)
logger = logging.getLogger(__name__)

from mongo_client import MongoDatabaseClient
from config_secrets import MONGO_URI

async def test():
    logger.info("=== DEBUGGING MONGO DB NAME ===")
    mc = MongoDatabaseClient(MONGO_URI)
    
    logger.info(f"Connected to Database: '{mc.db.name}'")
    logger.info(f"MONGO_URI: {MONGO_URI}")
    
    count = mc.tracks_collection.count_documents({})
    logger.info(f"Total Tracks in '{mc.db.name}': {count}")
    
    mood_count = mc.tracks_collection.count_documents({"mood": "Euphoric"})
    logger.info(f"Euphoric Tracks in '{mc.db.name}': {mood_count}")
    
    # Check if another DB exists?
    logger.info(f"Existing Databases: {mc.client.list_database_names()}")

if __name__ == "__main__":
    asyncio.run(test())
