import os
import sys
from pymongo import MongoClient

def audit_prod():
    try:
        uri = "mongodb://root:4f5cd00532af49b5941d6f6385b2e0bf@192.168.178.222:27017/?authSource=admin"
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        
        # Check 'yourparty' DB
        db = client['yourparty']
        print(f"--- DB: yourparty Audit ---")
        tracks_col = db['tracks']
        total = tracks_col.count_documents({})
        with_azid = tracks_col.count_documents({"azuracast_id": {"$exists": True, "$ne": None}})
        with_songid = tracks_col.count_documents({"song_id": {"$exists": True, "$ne": None}})
        
        print(f"Total Tracks: {total}")
        print(f"Tracks with 'azuracast_id': {with_azid}")
        print(f"Tracks with 'song_id': {with_songid}")
        
        if total > 0:
            sample = tracks_col.find_one()
            print(f"Sample Metadata: {sample.get('metadata', 'N/A')}")
            print(f"Sample File Path: {sample.get('file_path', 'N/A')}")

        # Check 'moods' collection
        moods_col = db['moods']
        mood_count = moods_col.count_documents({})
        unique_mood_songs = len(moods_col.distinct("song_id"))
        print(f"\nMoods tagged: {mood_count} across {unique_mood_songs} unique song_ids")

    except Exception as e:
        print(f"Audit failed: {e}")

if __name__ == "__main__":
    audit_prod()
