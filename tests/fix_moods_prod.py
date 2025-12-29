#!/usr/bin/env python3
import sys
import os
import asyncio
import logging
from dotenv import load_dotenv

# Load PROD Environment
sys.path.insert(0, '/opt/radio-api')
load_dotenv('/opt/radio-api/.env')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MoodFixer")

from mongo_client import MongoDatabaseClient
from config_secrets import MONGO_URI

MOOD_RULES = {
    "Euphoric": ["Dance", "House", "Pop", "Electronic", "Club", "Disco", "EDM"],
    "Chill": ["Lo-Fi", "Ambient", "Downtempo", "Lounge", "Jazz", "R&B", "Soul"],
    "Energy": ["Rock", "Metal", "Drum & Bass", "Techno", "Trance", "Dubstep"]
}

async def fix():
    logger.info("Connecting to MongoDB (Production)...")
    logger.info(f"URI: {MONGO_URI} (masked)")
    
    mc = MongoDatabaseClient(MONGO_URI)
    logger.info(f"Database: {mc.db.name}")
    
    # Sync Cursor
    cursor = mc.tracks_collection.find({}, {"genre": 1, "_id": 1, "title": 1})
    
    updates = 0
    stats = {"Euphoric": 0, "Chill": 0, "Energy": 0}
    
    for i, track in enumerate(cursor):
        genre = track.get("genre", "")
        title = track.get("title", "Unknown")
        
        if i < 10:
             logger.info(f"Sample [{i}]: Title='{title}' Genre='{genre}'")
        
        if not genre: continue
        
        assigned_mood = None
        for mood, keywords in MOOD_RULES.items():
            if any(k.lower() in genre.lower() for k in keywords):
                assigned_mood = mood
                break
        
        if assigned_mood:
             res = mc.tracks_collection.update_one(
                 {"_id": track["_id"]},
                 {"$set": {"mood": assigned_mood}}
             )
             if res.modified_count > 0 or res.matched_count > 0:
                 stats[assigned_mood] += 1
                 updates += 1
                 
    logger.info(f"Tagged {updates} tracks in DB '{mc.db.name}'.")
    logger.info(f"Stats: {stats}")

if __name__ == "__main__":
    asyncio.run(fix())
