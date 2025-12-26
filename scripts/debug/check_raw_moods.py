from mongo_client import MongoDatabaseClient
import os

mongo = MongoDatabaseClient(os.getenv("MONGO_URI", "mongodb://192.168.178.222:27017/yourparty"))

print("=== Raw Moods Collection Sample ===")
try:
    moods = list(mongo.moods_collection.find().limit(10))
    print(f"Found {len(moods)} mood documents (showing up to 10):")
    for m in moods:
        print(f"  song_id={m.get('song_id')}, mood={m.get('mood')}, title={m.get('metadata',{}).get('title','?')}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== Recent mood_next_votes ===")
try:
    votes = list(mongo.mood_next_votes_collection.find().sort("timestamp", -1).limit(10))
    print(f"Found {len(votes)} vote documents (showing up to 10):")
    for v in votes:
        print(f"  mood_next={v.get('mood_next')}, song_id={v.get('song_id')}, ts={v.get('timestamp')}")
except Exception as e:
    print(f"Error: {e}")
