import os
from pymongo import MongoClient
from collections import Counter
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GenreAnalyzer")

# Mongo URI
MONGO_URI = "mongodb://root:4f5cd00532af49b5941d6f6385b2e0bf@192.168.178.222:27017/yourparty?authSource=admin"

def analyze_library():
    try:
        client = MongoClient(MONGO_URI)
        db = client["yourparty"]
        collection = db["tracks"]
        
        count = collection.count_documents({})
        logger.info(f"Connected. Total Tracks: {count}")
        
        cursor = collection.find({})
        
        genres = []
        moods = []
        
        for i, track in enumerate(cursor):
            g = track.get("genre")
            
            # Fallback: Derive from Path
            if not g:
                rel_path = track.get("relative_path", "")
                if rel_path:
                    parts = rel_path.replace("\\", "/").split("/")
                    if len(parts) > 0:
                        top = parts[0]
                        if top == "Music" and len(parts) > 1:
                            # Check if next level is Artist or Genre?
                            # Log sample
                            if i % 100 == 0: logger.info(f"Music Path Sample: {rel_path}")
                            g = top # Keep as Music for stats, but we log samples
                        else:
                            g = top
            
            if not g: g = "Unknown"
            
            m = track.get("mood", "Unassigned")
            
            genres.append(g)
            if m: moods.append(m)
            
        genre_counts = Counter(genres).most_common(20)
        mood_counts = Counter(moods).most_common()
        
        logger.info("\n--- 🎵 TOP 20 GENRES ---")
        for g, c in genre_counts:
            logger.info(f"{g}: {c}")
            
        logger.info("\n--- 🏷️ CURRENT MOODS ---")
        for m, c in mood_counts:
            logger.info(f"{m}: {c}")
            
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    analyze_library()
