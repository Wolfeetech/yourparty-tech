
import random
import logging
from apps.api.mongo_client import MongoDatabaseClient
from apps.api.config_secrets import MONGO_URI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SeedMoods")

MOODS = ["ENERGY", "CHILL", "DARK", "GROOVE", "EUPHORIC"]

def seed_moods():
    mongo = MongoDatabaseClient(MONGO_URI)
    
    # buffers
    linked_tracks = list(mongo.tracks_collection.find({"azuracast_id": {"$exists": True}}))
    
    if not linked_tracks:
        logger.error("No linked tracks found! Run sync_azuracast_ids.py first.")
        return

    logger.info(f"Found {len(linked_tracks)} linked tracks. applying moods...")
    
    count = 0
    for track in linked_tracks:
        song_id = track.get("song_id")
        if not song_id: continue
        
        # Pick a random mood
        mood = random.choice(MOODS)
        
        # Submit mood
        mongo.submit_mood(song_id, mood=mood, user_id="system_test")
        count += 1
        
    logger.info(f"Seeded {count} tracks with random moods.")

if __name__ == "__main__":
    seed_moods()
