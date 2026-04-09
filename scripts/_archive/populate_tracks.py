#!/usr/bin/env python3
"""
Populate the 'tracks' collection with metadata from AzuraCast.
This is required for the API to return track metadata.
"""
import requests
from pymongo import MongoClient
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
MONGO_URI = "mongodb://root:4f5cd00532af49b5941d6f6385b2e0bf@192.168.178.222:27017"
AZURACAST_URL = "https://192.168.178.210"
AZURACAST_API_KEY = "9199dc63da623190:c9f8c3a22e25932753dd3f4d57fa0d9c"
STATION_ID = 1

def main():
    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    db = client.yourparty_radio
    tracks_collection = db.tracks
    
    print("Fetching song data from AzuraCast...")
    headers = {"Authorization": f"Bearer {AZURACAST_API_KEY}"}
    
    all_songs = {}
    
    # 1. Get song history (past plays)
    try:
        resp = requests.get(
            f"{AZURACAST_URL}/api/station/{STATION_ID}/history",
            headers=headers,
            verify=False,
            timeout=30
        )
        if resp.ok:
            history = resp.json()
            print(f"  Found {len(history)} history entries")
            for entry in history:
                song = entry.get("song", {})
                song_id = song.get("id")
                if song_id and song_id not in all_songs:
                    all_songs[song_id] = {
                        "song_id": song_id,
                        "file_path": song.get("path", ""),
                        "metadata": {
                            "title": song.get("title", "Unknown"),
                            "artist": song.get("artist", "Unknown"),
                            "album": song.get("album", ""),
                            "genre": song.get("genre", "")
                        }
                    }
    except Exception as e:
        print(f"  Error fetching history: {e}")
    
    # 2. Get current now playing
    try:
        resp = requests.get(
            f"{AZURACAST_URL}/api/nowplaying/{STATION_ID}",
            verify=False,
            timeout=10
        )
        if resp.ok:
            data = resp.json()
            
            # Now playing
            np = data.get("now_playing", {}).get("song", {})
            if np.get("id"):
                all_songs[np["id"]] = {
                    "song_id": np["id"],
                    "file_path": np.get("path", ""),
                    "metadata": {
                        "title": np.get("title", "Unknown"),
                        "artist": np.get("artist", "Unknown"),
                        "album": np.get("album", ""),
                        "genre": np.get("genre", "")
                    }
                }
            
            # Song history from nowplaying
            for entry in data.get("song_history", []):
                song = entry.get("song", {})
                if song.get("id"):
                    all_songs[song["id"]] = {
                        "song_id": song["id"],
                        "file_path": song.get("path", ""),
                        "metadata": {
                            "title": song.get("title", "Unknown"),
                            "artist": song.get("artist", "Unknown"),
                            "album": song.get("album", ""),
                            "genre": song.get("genre", "")
                        }
                    }
    except Exception as e:
        print(f"  Error fetching nowplaying: {e}")
    
    print(f"Total unique songs from AzuraCast: {len(all_songs)}")
    
    # Insert/Update tracks
    inserted = 0
    updated = 0
    
    for song_id, track_data in all_songs.items():
        result = tracks_collection.update_one(
            {"song_id": song_id},
            {"$set": track_data},
            upsert=True
        )
        if result.upserted_id:
            inserted += 1
        elif result.modified_count > 0:
            updated += 1
    
    print(f"\n=== Summary ===")
    print(f"Inserted: {inserted}")
    print(f"Updated: {updated}")
    print(f"Total tracks in collection: {tracks_collection.count_documents({})}")
    
    # Create indexes
    tracks_collection.create_index("song_id", unique=True)
    tracks_collection.create_index("file_path")
    print("Indexes created")
    
    client.close()

if __name__ == "__main__":
    main()
