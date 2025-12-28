
import os
import logging
from pymongo import MongoClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StationMigration")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://192.168.178.222:27017/")
DB_NAME = "yourparty"

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
