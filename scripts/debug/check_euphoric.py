from mongo_client import MongoDatabaseClient
import os

mongo = MongoDatabaseClient(os.getenv("MONGO_URI", "mongodb://192.168.178.222:27017/yourparty"))

print("=== Checking 'euphoric' tracks ===")
tracks = mongo.get_tracks_by_mood("euphoric")
print(f"Found {len(tracks)} tracks with mood 'euphoric'.")

if tracks:
    for t in tracks[:5]:
        meta = t.get('metadata', {})
        print(f"  - {meta.get('title', '?')} by {meta.get('artist', '?')}")
else:
    print("  (none)")

print("\n=== Checking Dominant Vote (last 60 min) ===")
dom = mongo.get_dominant_next_mood(time_window_minutes=60)
print(f"Dominant Next Mood: {dom}")
