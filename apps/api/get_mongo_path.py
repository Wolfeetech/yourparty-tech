from apps.api.mongo_client import MongoDatabaseClient
from apps.api.secrets import MONGO_URI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GetPath")

def get_path():
    mongo = MongoDatabaseClient(MONGO_URI)
    cursor = mongo.tracks_collection.find({"metadata.title": {"$regex": "Fade To Grey", "$options": "i"}})
    tracks = list(cursor)
    logger.info(f"FOUND {len(tracks)} MATCHES.")
    
    for track in tracks:
        path = track.get('file_path')
        song_id = track.get('song_id') or str(track.get('_id'))
        
        logger.info(f"\n--- TRACK: {track.get('metadata', {}).get('title')} ---")
        logger.info(f"PATH: {path}")
        logger.info(f"ID: {song_id}")
        
        moods = list(mongo.db.moods.aggregate([
            {"$match": {"song_id": song_id}},
            {"$group": {"_id": "$mood", "count": {"$sum": 1}}}
        ]))
        logger.info(f"VOTES: {moods}")
        logger.warning("Track not found in Mongo.")

if __name__ == "__main__":
    get_path()
