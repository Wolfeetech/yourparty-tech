import os
from pymongo import MongoClient
import datetime

# Hardcoded for verification script to avoid env var mess
MONGO_URI = "mongodb://root:4f5cd00532af49b5941d6f6385b2e0bf@192.168.178.222:27017/?authSource=admin"

print("--- CHECKING MONGODB ---\n")
try:
    client = MongoClient(MONGO_URI)
    db = client.yourparty
    
    # Check Mood Votes
    print("Querying 'mood_votes' collection...")
    latest_mood = db.mood_votes.find_one(sort=[('_id', -1)])
    
    if latest_mood:
        print(f"\n✅ LATEST VOTE FOUND:")
        print(f"Timestamp: {latest_mood.get('timestamp')}")
        print(f"Song ID:   {latest_mood.get('song_id')}")
        print(f"Mood:      {latest_mood.get('mood')}")
        print(f"User:      {latest_mood.get('user_id')}")
    else:
        print("\n❌ NO VOTES FOUND in 'mood_votes'.")

    # Check Tracks (Voting Candidates)
    print("\nQuerying 'tracks' collection (for Voting Candidates)...")
    track_count = db.tracks.count_documents({})
    print(f"Total Tracks: {track_count}")
    
    if track_count > 0:
        sample = db.tracks.find_one()
        print(f"Sample Track: {sample.get('title')} - {sample.get('artist')}")
    else:
        print("❌ NO TRACKS FOUND! Run /library/sync endpoint.")

except Exception as e:
    print(f"\n❌ ERROR: {e}")

print("\n--- CHECK COMPLETE ---")
