
import requests
import json
import logging
import sys
from typing import Dict, List, Optional

from apps.api.secrets import (
    MONGO_URI, 
    AZURACAST_API_URL, 
    AZURACAST_API_KEY, 
    AZURACAST_STATION_ID
)
from apps.api.mongo_client import MongoDatabaseClient

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Constants
MOOD_PLAYLIST_PREFIX = "Mo:"
MOODS = ["ENERGY", "CHILL", "DARK", "GROOVE", "EUPHORIC"]
HEADERS = {"Authorization": f"Bearer {AZURACAST_API_KEY}"}

def get_azura_playlists() -> Dict[str, int]:
    """Fetch existing playlists from AzuraCast."""
    url = f"{AZURACAST_API_URL}/station/{AZURACAST_STATION_ID}/playlists"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10, verify=False)
        resp.raise_for_status()
        playlists = resp.json()
        # Map Playlist Name -> ID
        return {p["name"]: p["id"] for p in playlists}
    except Exception as e:
        logger.error(f"Failed to fetch playlists: {e}")
        return {}

def create_azura_playlist(name: str) -> Optional[int]:
    """Create a new playlist in AzuraCast."""
    url = f"{AZURACAST_API_URL}/station/{AZURACAST_STATION_ID}/playlists"
    payload = {
        "name": name,
        "is_enabled": True,
        "type": "default", # Standard rotation
        "weight": 3        # Default weight
    }
    try:
        resp = requests.post(url, headers=HEADERS, json=payload, timeout=10, verify=False)
        resp.raise_for_status()
        data = resp.json()
        logger.info(f"Created playlist '{name}' (ID: {data['id']})")
        return data['id']
    except Exception as e:
        logger.error(f"Failed to create playlist '{name}': {e}")
        if hasattr(e, 'response') and e.response:
             logger.error(f"Response: {e.response.text}")
        return None

def get_azura_media_id(mongo_song_id: str, db_client: MongoDatabaseClient) -> Optional[int]:
    """Retrieve AzuraCast Media ID from Mongo using Song ID."""
    # Assuming sync_azuracast_ids.py has run, the 'azuracast_id' should be in the 'songs' collection 
    # or retrievable via valid 'path'.
    # Simplified: Look up song in DB
    song = db_client.db.songs.find_one({"_id": mongo_song_id})
    if song and "azuracast_id" in song:
        return song["azuracast_id"]
    return None

def sync_playlists():
    try:
        mongo = MongoDatabaseClient(MONGO_URI)
    except Exception:
        logger.error("Failed to connect to Mongo")
        return

    existing_playlists = get_azura_playlists()
    
    for mood in MOODS:
        playlist_name = f"{MOOD_PLAYLIST_PREFIX}{mood}"
        playlist_id = existing_playlists.get(playlist_name)
        
        # Create if missing
        if not playlist_id:
            logger.info(f"Playlist '{playlist_name}' missing. Creating...")
            playlist_id = create_azura_playlist(playlist_name)
        
        if not playlist_id:
            continue

        # Get Tracks with this mood (simple majority or high confidence)
        # Using a specialized query or aggregation from Mongo
        # For prototype: Get all songs where 'top_mood' == mood
        tracks = list(mongo.db.songs.find({"top_mood": mood}))
        logger.info(f"Found {len(tracks)} tracks for mood {mood}")

        # In a real sync, we would diff the playlist content.
        # For now, we are just ENSURING the playlist exists and logging what would be added.
        # To strictly Manage media, we'd need to use the /playlist/{id}/media endpoint
        
        valid_media_ids = []
        for track in tracks:
            az_id = track.get("azuracast_id")
            if az_id:
                valid_media_ids.append(az_id)
        
        if valid_media_ids:
            logger.info(f"-> Should ensure media IDs {valid_media_ids} are in playlist {playlist_id}")
            # TODO: Implement accurate PUT/POST to AzuraCast playlist media endpoint
            # This is complex because AzuraCast API for playlist media management requires specific formatting
            # For this MVP step, ensuring the Playlist Exists is the success criteria.

if __name__ == "__main__":
    sync_playlists()
