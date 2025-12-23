import os
import time
import logging
from mongo_client import MongoDatabaseClient
from tag_writer import write_metadata_to_file

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("RatingSync")

# Load .env manually if needed
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    logger.info(f"Loading env from {env_path}")
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, _, value = line.partition('=')
                if key and value:
                     os.environ[key.strip()] = value.strip().strip('"').strip("'")

# Configuration
# Construct URI from env
mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri or "root:yourparty" in mongo_uri: # Default/Placeholder check
    user = os.getenv("MONGO_INITDB_ROOT_USERNAME", "root")
    pwd = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "")
    host = os.getenv("MONGO_HOST", "192.168.178.222")
    port = os.getenv("MONGO_PORT", "27017")
    if user and pwd:
        # Check if authSource is needed (often 'admin')
        mongo_uri = f"mongodb://{user}:{pwd}@{host}:{port}/?authSource=admin"
        logger.info(f"Constructed URI: mongodb://{user}:****@{host}:{port}/?authSource=admin")
    else:
        mongo_uri = f"mongodb://{host}:{port}/"

MONGO_URI = mongo_uri
DB_NAME = "radio_ratings"

def sync_db_to_files():
    """
    Fetch all rated tracks from MongoDB and write their ratings/moods
    into the actual ID3 tags of the MP3 files.
    """
    logger.info("Starting Sync: MongoDB -> ID3 Tags")
    
    try:
        db = MongoDatabaseClient(MONGO_URI, DB_NAME)
        # We need a robust 'init' potentially if async, but MongoDatabaseClient seems synchronous for basic ops?
        # Looking at api.py, it uses `await db.init()` in startup, but the class __init__ creates the client.
        # Let's hope basic ops work without async init if connection is direct.
        # Actually mongo_client.py uses standard MongoClient (sync) unless it wrapped motor?
        # It imports `pymongo.MongoClient`, so it is synchronous.
        
        tracks = db.get_all_rated_tracks(min_rating=0.0) # Get everything
        logger.info(f"Found {len(tracks)} tracks with ratings in DB.")
        
        success_count = 0
        fail_count = 0
        
        for track in tracks:
            # Data structure from get_all_rated_tracks:
            # {
            #   "song_id": "...",
            #   "file_path": "...",
            #   "rating": { ... },
            #   "metadata": { ... }
            # }
            
            song_id = track.get('song_id')
            file_path = track.get('file_path')
            avg_rating = track.get('rating', {}).get('average', 0)
            
            if not song_id:
                logger.warning("Empty song_id in track record")
                continue

            if not file_path:
                # Fallback: Try to look it up if missing
                logger.warning(f"No file_path for song_id: {song_id}. Attempting fallback lookup...")
                
                # JIT Client Init for fallback
                try:
                    from azuracast_client import AzuraCastClient
                    ac_url = os.getenv("AZURACAST_URL", "http://192.168.178.210")
                    ac_key = os.getenv("AZURACAST_API_KEY", "9199dc63da6223190:c9f8c3a22e25932753dd3f4d57fa0d9c")
                    client = AzuraCastClient(ac_url, ac_key, 1) # Station 1
                    
                    # 1. Ask AzuraCast who this ID is
                    # There isn't a direct "get media by unique_id" easily always, but let's try to search or just rely on the fact 
                    # we can't easily get it. Wait, we can iterate 'now_playing' history? No.
                    # Best bet: We iterate our LOCAL tracks DB and try to match? No we don't know the title.
                    # We only have song_id.
                    # Let's try `get_station_media` filtering? No efficiently.
                    
                    # Actually, if we can't resolve ID to Metadata, we are stuck.
                    # BUT, does AzuraCast have an endpoint for simple metadata lookup?
                    # /api/station/{station_id}/media/{media_id} -> This takes the ID (int) usually.
                    # If 'song_id' is the unique_hash, we might be out of luck via standard API.
                    
                    # Workaround:
                    # Let's hope users only rate things visible in NowPlaying.
                    # We can fetch NowPlaying history?
                    history = client.get_now_playing() # This returns current + history
                    found_meta = None
                    
                    # Check Current
                    np_song = history.get('now_playing', {}).get('song', {})
                    if str(np_song.get('id')) == song_id:
                         found_meta = np_song
                    
                    # Check History
                    if not found_meta:
                        for item in history.get('song_history', []):
                             s = item.get('song', {})
                             if str(s.get('id')) == song_id:
                                  found_meta = s
                                  break
                    
                    if found_meta:
                        title = found_meta.get('title')
                        artist = found_meta.get('artist')
                        logger.info(f"Resolved ID {song_id} to '{title}' - '{artist}' via History.")
                        
                        # Search Local DB by Title/Artist
                        # Use regex for leniency
                        import re
                        query = {
                            "metadata.title": {"$regex": re.escape(title), "$options": "i"},
                            "metadata.artist": {"$regex": re.escape(artist), "$options": "i"}
                        }
                        match = db.tracks_collection.find_one(query)
                        if match and match.get('file_path'):
                             file_path = match.get('file_path')
                             logger.info(f"Found match in local DB: {file_path}")
                except Exception as e:
                    logger.error(f"Fallback lookup failed: {e}")

            if not file_path:
                logger.warning(f"Still no file_path for song_id: {song_id}")
                fail_count += 1
                continue
            if not os.path.exists(file_path):
                # Try to map /mnt/music_hdd path if stored differently
                # Check for common path variations if running in container vs local
                container_path = file_path.replace("/mnt/music_hdd", "/var/radio/music")
                if os.path.exists(container_path):
                     file_path = container_path
                else:
                    # Broken Symlink Fix: /var/radio/music/Music -> /var/radio/music/radio_library/Music
                    if "/var/radio/music/Music/" in file_path:
                        fix_path = file_path.replace("/var/radio/music/Music/", "/var/radio/music/radio_library/Music/")
                        if os.path.exists(fix_path):
                             file_path = fix_path
                        else:
                             # Double check if it was mapped from outside (AzuraCast path Music/...)
                             # AzuraCast path: Music/_input/...
                             # Local path: /var/radio/music/radio_library/Music/_input/...
                             # Just try constructing it
                             base_name = file_path.split("/Music/")[-1]
                             fix_path_2 = f"/var/radio/music/radio_library/Music/{base_name}"
                             if os.path.exists(fix_path_2):
                                 file_path = fix_path_2
                             else:
                                 logger.warning(f"File not found on disk (tried {file_path}, {fix_path}): {file_path}")
                                 fail_count += 1
                                 continue
                    else:
                        logger.warning(f"File not found on disk: {file_path}")
                        fail_count += 1
                        continue
                
            # Fetch Moods
            mood_data = db.get_song_moods(song_id)
            top_mood = mood_data.get('top_mood')
            
            # Write Tags
            if write_metadata_to_file(file_path, rating=avg_rating, mood=top_mood):
                success_count += 1
            else:
                fail_count += 1
                
        logger.info(f"Sync Complete. Success: {success_count}, Failed: {fail_count}")
        
    except Exception as e:
        logger.error(f"Critical Sync Error: {e}")

if __name__ == "__main__":
    # Continuous loop or single run? 
    # Let's do single run for now, meant to be cron-job or triggered.
    sync_db_to_files()
