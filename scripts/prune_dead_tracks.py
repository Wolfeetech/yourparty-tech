import logging
import argparse
from pymongo import MongoClient

# Setup
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("DB_Pruner")

MONGO_URI = "mongodb://root:4f5cd00532af49b5941d6f6385b2e0bf@192.168.178.222:27017/?authSource=admin"

def prune_dead_tracks(dry_run=True):
    try:
        client = MongoClient(MONGO_URI)
        db = client["yourparty"]
        tracks = db["tracks"]
        
        query = {"azuracast_id": None}
        count = tracks.count_documents(query)
        
        logger.info(f"🔎 Found {count} 'Zombie Tracks' (No AzuraCast ID).")
        
        if count == 0:
            logger.info("✅ Database is clean! Nothing to prune.")
            return

        if dry_run:
            logger.info("🚧 [DRY RUN] No changes made. Run with --force to delete.")
        else:
            result = tracks.delete_many(query)
            logger.info(f"🗑️ Deleted {result.deleted_count} tracks.")
            
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Actually delete the tracks")
    args = parser.parse_args()
    
    prune_dead_tracks(dry_run=not args.force)
