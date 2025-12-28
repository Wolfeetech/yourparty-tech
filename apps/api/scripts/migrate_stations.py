
import os
import logging
from pymongo import MongoClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StationMigration")

# Load env if possible or use the one found
from dotenv import load_dotenv
load_dotenv("/app/.env")

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    # Fallback to the one found in logs just in case env loading fails
    MONGO_URI = "mongodb://root:4f5cd00532af49b5941d6f6385b2e0b@192.168.178.222:27017/yourparty_radio?authSource=admin"

DB_NAME = "yourparty_radio" # Updated from .env

def migrate():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        
        collections_to_migrate = [
            "moods",
            "mood_next_votes",
            "next_track_votes",
            "votes",
            "rating_events" 
        ]
        
        for col_name in collections_to_migrate:
            if col_name not in db.list_collection_names():
                logger.info(f"Skipping {col_name} (not found)")
                continue

            col = db[col_name]
            
            # Update docs missing station_id
            result = col.update_many(
                {"station_id": {"$exists": False}},
                {"$set": {"station_id": 1}}
            )
            
            logger.info(f"Migrated {col_name}: Updated {result.modified_count} documents.")
            
    except Exception as e:
        logger.error(f"Migration Failed: {e}")

if __name__ == "__main__":
    migrate()
