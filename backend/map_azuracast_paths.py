import os
import logging
from mongo_client import MongoDatabaseClient
from azuracast_client import AzuraCastClient

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Mapper")

# Load Env
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, _, value = line.partition('=')
                if key and value:
                     os.environ[key.strip()] = value.strip().strip('"').strip("'")

# Config
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI or "root:yourparty" in MONGO_URI:
    user = os.getenv("MONGO_INITDB_ROOT_USERNAME", "root")
    pwd = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "")
    host = os.getenv("MONGO_HOST", "192.168.178.222")
    port = os.getenv("MONGO_PORT", "27017")
    MONGO_URI = f"mongodb://{user}:{pwd}@{host}:{port}/?authSource=admin"

AC_URL = os.getenv("AZURACAST_URL", "http://192.168.178.210")
AC_KEY = os.getenv("AZURACAST_API_KEY", "9199dc63da6223190:c9f8c3a22e25932753dd3f4d57fa0d9c")
STATION_ID = 1

def run_mapping():
    logger.info("Starting AzuraCast -> MongoDB Path Mapping...")
    
    # Init Clients
    mongo = MongoDatabaseClient(MONGO_URI)
    ac = AzuraCastClient(AC_URL, AC_KEY, STATION_ID)
    
    # Fetch all media from AzuraCast
    logger.info("Fetching media from AzuraCast...")
    try:
        media_list = ac.get_station_media()
        logger.info(f"Received {len(media_list)} tracks from AzuraCast.")
    except Exception as e:
        logger.error(f"Failed to fetch media: {e}")
        return

    updated_count = 0
    
    for item in media_list:
        song_id = item.get('unique_id')
        # Path in AzuraCast might be relative to media dir, e.g. "Techno/Song.mp3"
        # We need to map this to our NFS mount: /var/radio/music/Techno/Song.mp3
        ac_path = item.get('path', '')
        
        if not song_id or not ac_path:
            continue
            
        # Construct local path
        # Assuming AzuraCast 'path' is relative to station media root
        local_path = os.path.join("/var/radio/music", ac_path)
        
        # Update MongoDB
        try:
            mongo.tracks_collection.update_one(
                {"song_id": song_id},
                {"$set": {
                    "file_path": local_path,
                    "metadata": {
                        "title": item.get('title'),
                        "artist": item.get('artist'),
                        "album": item.get('album')
                    }
                }},
                upsert=True
            )
            updated_count += 1
        except Exception as e:
             logger.error(f"Error updating {song_id}: {e}")
             
    logger.info(f"Mapping Complete. Updated {updated_count} tracks.")

if __name__ == "__main__":
    run_mapping()
