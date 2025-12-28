
import os
import uuid
import logging
from dotenv import load_dotenv
from apps.api.mongo_client import MongoDatabaseClient

load_dotenv('/opt/radio-api/.env')
# Force correct DB
db = MongoDatabaseClient(os.getenv("MONGO_URI"), database_name="yourparty").db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FixSongIDs")

def fix():
    logger.info("Checking for tracks without song_id...")
    missing_count = db.tracks.count_documents({"song_id": {"$exists": False}})
    null_count = db.tracks.count_documents({"song_id": None})
    
    logger.info(f"Missing: {missing_count}, Null: {null_count}")
    
    if missing_count == 0 and null_count == 0:
        logger.info("All tracks have song_ids.")
        return

    # Fix nulls
    cursor = db.tracks.find({"song_id": None})
    fixed = 0
    for t in cursor:
        new_id = str(uuid.uuid4())
        db.tracks.update_one({"_id": t["_id"]}, {"$set": {"song_id": new_id}})
        fixed += 1
        if fixed % 100 == 0:
             logger.info(f"Fixed {fixed} null song_ids...")

    # Fix missing
    cursor = db.tracks.find({"song_id": {"$exists": False}})
    for t in cursor:
        new_id = str(uuid.uuid4())
        db.tracks.update_one({"_id": t["_id"]}, {"$set": {"song_id": new_id}})
        fixed += 1
        if fixed % 100 == 0:
             logger.info(f"Fixed {fixed} missing song_ids...")
             
    logger.info(f"Done. Fixed {fixed} tracks.")

if __name__ == "__main__":
    fix()
