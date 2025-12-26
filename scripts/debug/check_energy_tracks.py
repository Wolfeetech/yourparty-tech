from mongo_client import MongoDatabaseClient
import os

mongo = MongoDatabaseClient(os.getenv("MONGO_URI", "mongodb://192.168.178.222:27017/yourparty"))
print("Checking 'energy' tracks...")
tracks = mongo.get_tracks_by_mood("energy")
print(f"Found {len(tracks)} tracks with mood 'energy'.")

if tracks:
    print(f"Example: {tracks[0].get('metadata', {}).get('title', 'Unknown')}")
else:
    print("⚠️ No tracks found! Auto-DJ cannot fulfill 'Energy' vote.")

# Check dominant mood too
print("\nChecking Dominant Vote...")
dom = mongo.get_dominant_next_mood(time_window_minutes=60)
print(f"Dominant Mood (last 60m): {dom}")
