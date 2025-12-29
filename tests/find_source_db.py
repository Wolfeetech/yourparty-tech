#!/usr/bin/env python3
import sys
import os
import asyncio
import logging
from dotenv import load_dotenv

# Load PROD Environment
sys.path.insert(0, '/opt/radio-api')
load_dotenv('/opt/radio-api/.env')

logging.basicConfig(level=logging.INFO, stream=sys.stdout, force=True)
logger = logging.getLogger("DBFinder")

from mongo_client import MongoDatabaseClient, MongoClient
from config_secrets import MONGO_URI

async def find_db():
    logger.info("Connecting to MongoDB...")
    client = MongoClient(MONGO_URI)
    dbs = client.list_database_names()
    logger.info(f"Databases: {dbs}")
    
    candidates = ['yourparty', 'music_library', 'yourparty_radio', 'test', 'radio']
    
    for db_name in dbs:
        if db_name in ['admin', 'config', 'local']: continue
        
        logger.info(f"--- Inspecting '{db_name}' ---")
        db = client[db_name]
        try:
            count = db.tracks.count_documents({})
            tagged = db.tracks.count_documents({"mood": {"$exists": True}})
            synced = db.tracks.count_documents({"azuracast_id": {"$exists": True}})
            logger.info(f"  Tracks: {count}, Tagged: {tagged}, Synced: {synced}")
            
            if count > 0:
                sample = db.tracks.find_one({})
                logger.info(f"  Sample: Title='{sample.get('title')}', Genre='{sample.get('genre')}', Mood='{sample.get('mood')}'")
        except Exception as e:
            logger.info(f"  Error inspecting: {e}")

if __name__ == "__main__":
    asyncio.run(find_db())
