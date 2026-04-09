import os
import logging
from apps.api.mongo_client import MongoDatabaseClient
from apps.api.secrets import MONGO_URI
import mutagen

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VerifyTrack")

def verify_track(search_term="Fade To Grey"):
    # 1. Connect to Mongo
    mongo = MongoDatabaseClient(MONGO_URI)
    logger.info(f"Searching Mongo for '{search_term}'...")
    
    # Query
    query = {
        "$or": [
            {"metadata.title": {"$regex": search_term, "$options": "i"}},
            {"metadata.artist": {"$regex": search_term, "$options": "i"}}
        ]
    }
    
    tracks = list(mongo.tracks_collection.find(query))
    logger.info(f"Found {len(tracks)} matches in MongoDB.")
    
    for t in tracks:
        meta = t.get('metadata', {})
        song_id = t.get('song_id') or str(t.get('_id'))
        path = t.get('file_path')
        
        logger.info(f"\n--- MATCH: {meta.get('artist')} - {meta.get('title')} ---")
        logger.info(f"Mongo ID: {song_id}")
        
        # Check Ratings in Mongo
        rating = mongo.get_track_rating(song_id)
        logger.info(f"Mongo Rating: {rating}")
        
        # Check Moods in Mongo
        pass
        # mongo.get_song_moods is not printed to avoid clutter if empty
        
        # 2. Check File Tags
        logger.info(f"Raw Mongo Path: {path}")
        
        win_path = None
        if path:
            norm_path = path.replace('/', '\\')
            
            if os.path.exists(path):
                win_path = path
            elif norm_path.startswith('\\mnt\\data\\'):
                # Linux container path to Windows Z:
                win_path = 'Z:' + norm_path[10:]
            elif not ':' in norm_path and not norm_path.startswith('\\'):
                # Relative path
                win_path = os.path.join('Z:\\', norm_path)
            elif norm_path.startswith('\\'):
                 # Absolute without drive
                win_path = 'Z:' + norm_path
        
        if win_path:
            logger.info(f"Checking Windows Path: {win_path}")
            
            if not os.path.exists(win_path):
                # Fallback search
                filename = os.path.basename(win_path)
                logger.info(f"Path not found. Searching Z: for filename: {filename}...")
                for root, _, files in os.walk("Z:\\"):
                    if filename in files:
                        win_path = os.path.join(root, filename)
                        logger.info(f"Found at alternative location: {win_path}")
                        break
            
            if os.path.exists(win_path):
                try:
                    audio = mutagen.File(win_path)
                    logger.info("--- ID3 TAGS ---")
                    if audio and hasattr(audio, 'tags'):
                        for key, val in audio.tags.items():
                            if 'TXXX' in key or 'POP' in key or 'COMM' in key or 'mood' in key.lower():
                                logger.info(f"{key}: {val}")
                            if key in ['TCON', 'GENRE']:
                                logger.info(f"Genre: {val}")
                    else:
                        logger.info("No tags found.")
                except Exception as e:
                    logger.error(f"Error: {e}")
            else:
                 logger.warning("File NOT found on disk (Z:).")

if __name__ == "__main__":
    verify_track("Fade To Grey")
