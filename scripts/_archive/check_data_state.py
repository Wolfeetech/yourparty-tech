
import os
import sys
# Add path to find apps module if run from scripts/
sys.path.append('/opt/radio-api')

from dotenv import load_dotenv
from apps.api.mongo_client import MongoDatabaseClient

load_dotenv('/opt/radio-api/.env')
# Force correct DB
db_client = MongoDatabaseClient(os.getenv("MONGO_URI"), database_name="yourparty")
db = db_client.db

print("=== DATA STATE CHECK ===")
try:
    total_tracks = db.tracks.count_documents({})
    synced_tracks = db.tracks.count_documents({"azuracast_id": {"$exists": True}})
    total_moods = db.moods.count_documents({})
    
    print(f"Total Tracks: {total_tracks}")
    print(f"Synced Tracks (AC_ID): {synced_tracks}")
    print(f"Total Mood Tags: {total_moods}")
    
    if total_moods > 0:
        print("Sample Moods:")
        for m in db.moods.find().limit(5):
             # Try to find corresponding track
             song_id = m.get('song_id')
             track = db.tracks.find_one({"song_id": song_id})
             synced_status = "SYNCED" if track and track.get('azuracast_id') else "NOT SYNCED"
             print(f" - Mood: {m.get('mood')} | SongID: {song_id} | {synced_status}")

except Exception as e:
    print(f"Error: {e}")
