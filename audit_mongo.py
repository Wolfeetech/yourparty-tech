import os
import sys
from pathlib import Path

# Add apps/api to path
sys.path.append(str(Path.cwd() / "apps" / "api"))
from mongo_client import MongoDatabaseClient

def audit():
    try:
        db = MongoDatabaseClient()
        total = db.db.tracks.count_documents({})
        with_azid = db.db.tracks.count_documents({"azuracast_id": {"$exists": True, "$ne": None}})
        with_songid = db.db.tracks.count_documents({"song_id": {"$exists": True, "$ne": None}})
        with_mood = db.db.moods.distinct("song_id")
        
        print(f"--- MongoDB Audit ---")
        print(f"Total Tracks in 'tracks' collection: {total}")
        print(f"Tracks with 'azuracast_id' (Media ID): {with_azid}")
        print(f"Tracks with 'song_id' (AC Unique ID): {with_songid}")
        print(f"Unique songs with at least one mood tag: {len(with_mood)}")
        
        # Check mood distribution
        pipeline = [
            {"$group": {"_id": "$mood", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        mood_dist = list(db.db.moods.aggregate(pipeline))
        print("\n--- Mood Distribution ---")
        for m in mood_dist:
            print(f"  {m['_id']}: {m['count']}")
            
    except Exception as e:
        print(f"Error during audit: {e}")

if __name__ == "__main__":
    audit()
