import os
from pymongo import MongoClient
import datetime

# Hardcoded for verification script to avoid env var mess
from apps.api.secrets import MONGO_URI

print("--- CHECKING MONGODB ---\n")
try:
    client = MongoClient(MONGO_URI)
    db = client.radio_ratings
    
    # Check Mood Votes
    print("Querying 'moods' collection...")
    latest_mood = db.moods.find_one(sort=[('_id', -1)])
    
    if latest_mood:
        print(f"\n✅ LATEST VOTE FOUND:")
        print(f"Timestamp: {latest_mood.get('timestamp')}")
        print(f"Song ID:   {latest_mood.get('song_id')}")
        print(f"Mood:      {latest_mood.get('mood')}")
        print(f"User:      {latest_mood.get('user_id')}")
    else:
        print("\n❌ NO VOTES FOUND in 'moods'.")

    # Check Tracks (Voting Candidates)
    print("\nQuerying 'tracks' collection...")
    track_count = db.tracks.count_documents({})
    print(f"Total Tracks: {track_count}")
    
    if track_count > 0:
        sample = db.tracks.find_one()
        print(f"Sample Track (path): {sample.get('file_path')}")
        print(f"Sample Track (meta): {sample.get('metadata')}")

    # Check Song Metadata (User's new source)
    print("\nQuerying 'song_metadata' collection...")
    meta_count = db.song_metadata.count_documents({})
    print(f"Total Metadata Docs: {meta_count}")

    if meta_count > 0:
        sample_meta = db.song_metadata.find_one()
        print(f"Sample Metadata: {sample_meta}")
    else:
        print("❌ 'song_metadata' is EMPTY! User's code queries this.")

except Exception as e:
    print(f"\n❌ ERROR: {e}")

print("\n--- CHECK COMPLETE ---")
