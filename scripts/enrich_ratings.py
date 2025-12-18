#!/usr/bin/env python3
"""
Enrich existing ratings with metadata from AzuraCast media library.
Queries all songs from AzuraCast and updates MongoDB ratings that match by song_id.
"""
import os
import hashlib
import requests
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables (NO HARDCODED SECRETS!)
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_USER = os.getenv("MONGO_USER", "")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "")
MONGO_DB = os.getenv("MONGO_DB", "yourparty_radio")

# Build MongoDB URI from components
if MONGO_USER and MONGO_PASSWORD:
    MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}"
else:
    MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}"

AZURACAST_URL = os.getenv("AZURACAST_URL")
AZURACAST_API_KEY = os.getenv("AZURACAST_API_KEY")
STATION_ID = int(os.getenv("AZURACAST_STATION_ID", "1"))

# Validate required environment variables
if not AZURACAST_URL or not AZURACAST_API_KEY:
    raise ValueError("AZURACAST_URL and AZURACAST_API_KEY environment variables are required!")

def get_song_id(title: str, artist: str) -> str:
    """Generate song_id hash matching AzuraCast format"""
    combined = f"{title or ''}{artist or ''}"
    return hashlib.md5(combined.encode('utf-8')).hexdigest()

def main():
    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    db = client.yourparty
    
    # Fetch all media from AzuraCast
    print(f"Fetching media library from AzuraCast...")
    headers = {"Authorization": f"Bearer {AZURACAST_API_KEY}"}
    
    try:
        response = requests.get(
            f"{AZURACAST_URL}/api/station/{STATION_ID}/files",
            headers=headers,
            verify=False,
            timeout=30
        )
        response.raise_for_status()
        media_list = response.json()
        print(f"Found {len(media_list)} tracks in AzuraCast library")
    except Exception as e:
        print(f"Error fetching media: {e}")
        return
    
    # Build lookup table: song_id -> metadata
    song_lookup = {}
    for media in media_list:
        title = media.get("title", "")
        artist = media.get("artist", "")
        if title or artist:
            song_id = get_song_id(title, artist)
            song_lookup[song_id] = {
                "title": title or "Unknown",
                "artist": artist or "Unknown",
                "album": media.get("album", ""),
                "genre": media.get("genre", ""),
                "path": media.get("path", "")
            }
    
    print(f"Built lookup table with {len(song_lookup)} unique song_ids")
    
    # Get all ratings from MongoDB
    ratings = list(db.ratings.find({}))
    print(f"Found {len(ratings)} ratings in MongoDB")
    
    updated = 0
    not_found = 0
    already_has_metadata = 0
    
    for rating in ratings:
        song_id = rating.get("_id")
        existing_title = rating.get("title", "")
        
        # Skip if already has valid metadata
        if existing_title and existing_title not in ["Unknown", "Unknown Track", ""]:
            already_has_metadata += 1
            continue
        
        # Look up in AzuraCast data
        if song_id in song_lookup:
            metadata = song_lookup[song_id]
            db.ratings.update_one(
                {"_id": song_id},
                {"$set": metadata}
            )
            print(f"  Updated: {metadata['artist']} - {metadata['title']}")
            updated += 1
        else:
            not_found += 1
    
    print(f"\n=== Summary ===")
    print(f"Updated: {updated}")
    print(f"Already had metadata: {already_has_metadata}")
    print(f"Not found in AzuraCast: {not_found}")
    
    client.close()

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
