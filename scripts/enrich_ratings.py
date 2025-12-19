#!/usr/bin/env python3
"""
Enrich existing ratings with metadata from AzuraCast.
Uses the station history endpoint to match song_ids directly.
"""
import os
from datetime import datetime
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
    
    # Get all song_ids from ratings that need metadata
    ratings = list(db.ratings.find({}))
    print(f"Found {len(ratings)} ratings in MongoDB")
    
    # Build set of song_ids that need enrichment
    needs_metadata = {}
    for r in ratings:
        song_id = r.get("_id")
        title = r.get("title", "")
        if not title or title in ["Unknown", "Unknown Track", ""]:
            needs_metadata[song_id] = r
    
    print(f"{len(needs_metadata)} ratings need metadata enrichment")
    
    if not needs_metadata:
        print("All ratings already have metadata!")
        return
    
    # Fetch history from AzuraCast (last 1000 plays)
    print("Fetching song history from AzuraCast...")
    headers = {"Authorization": f"Bearer {AZURACAST_API_KEY}"}
    
    history_songs = {}
    
    # Get song history
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
                if song_id and song_id not in history_songs:
                    history_songs[song_id] = {
                        "title": song.get("title", "Unknown"),
                        "artist": song.get("artist", "Unknown"),
                        "album": song.get("album", ""),
                        "genre": song.get("genre", "")
                    }
    except Exception as e:
        print(f"  Error fetching history: {e}")
    
    # Also get nowplaying and queue
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
                history_songs[np["id"]] = {
                    "title": np.get("title", "Unknown"),
                    "artist": np.get("artist", "Unknown"),
                    "album": np.get("album", ""),
                    "genre": np.get("genre", "")
                }
            
            # Song history from nowplaying
            for entry in data.get("song_history", []):
                song = entry.get("song", {})
                if song.get("id"):
                    history_songs[song["id"]] = {
                        "title": song.get("title", "Unknown"),
                        "artist": song.get("artist", "Unknown"),
                        "album": song.get("album", ""),
                        "genre": song.get("genre", "")
                    }
    except Exception as e:
        print(f"  Error fetching nowplaying: {e}")
    
    print(f"Total unique songs from AzuraCast: {len(history_songs)}")
    
    # Update ratings
    updated = 0
    not_found = 0
    
    for song_id, rating in needs_metadata.items():
        if song_id in history_songs:
            metadata = history_songs[song_id]
            # Correct Logic: Update 'tracks' collection where API looks for metadata
            # We use upsert=True to ensure the track record exists even if not previously scanned
            db.tracks.update_one(
                {"song_id": song_id},
                {"$set": {
                    "metadata": metadata,
                    "last_updated": datetime.utcnow()
                }},
                upsert=True
            )
            print(f"  ✓ Synced Track: {metadata['artist']} - {metadata['title']}")
            updated += 1
        else:
            not_found += 1
    
    print(f"\n=== Summary ===")
    print(f"Updated: {updated}")
    print(f"Not found in history: {not_found}")
    print(f"(Tracks not in recent history will get metadata when played again)")
    
    client.close()

if __name__ == "__main__":
    main()
