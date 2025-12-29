import requests
import json
import logging
import sys
import os
import urllib3
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load env - prefer script location, fallback to default
load_dotenv('/opt/radio-api/.env')
load_dotenv()

# Configuration
MONGO_URI = os.getenv("MONGO_URI")
# Fallback to local IP if not set
AZURACAST_API_URL = os.getenv("AZURACAST_URL", "https://radio.yourparty.tech/api").rstrip('/')
if AZURACAST_API_URL.startswith('http:'):
    AZURACAST_API_URL = AZURACAST_API_URL.replace('http:', 'https:')

if not AZURACAST_API_URL.endswith('/api'):
    AZURACAST_API_URL += '/api'

AZURACAST_API_KEY = os.getenv("AZURACAST_API_KEY")
AZURACAST_STATION_ID = os.getenv("AZURACAST_STATION_ID", 1)

from apps.api.mongo_client import MongoDatabaseClient

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Suppress SSL Warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

        # Get Tracks with this mood
        # We use the moods collection to find song_ids, then get tracks.
        # This matches the schema in mongo_client.py
        mood_docs = list(mongo.db.moods.find({"mood": mood}))
        song_ids = [d['song_id'] for d in mood_docs if 'song_id' in d]
        
        # Get AzuraCast IDs for these song_ids from 'tracks' collection
        tracks = list(mongo.db.tracks.find({"song_id": {"$in": song_ids}}))
        logger.info(f"Found {len(tracks)} synced tracks for mood {mood}")

        valid_media_ids = []
        for track in tracks:
            # Check for azuracast_id in track document
            # Note: This field needs to be populated by sync_azuracast_ids.py or similar
            az_id = track.get("azuracast_id")
            if az_id:
                valid_media_ids.append(az_id)
        
        if valid_media_ids:
            logger.info(f"-> Syncing {len(valid_media_ids)} tracks to playlist {playlist_id}...")
            
            # Initialize Client
            from apps.api.azuracast_client import AzuraCastClient
            client = AzuraCastClient(AZURACAST_API_URL, AZURACAST_API_KEY, AZURACAST_STATION_ID)
            
            # Use batch update
            success = client.replace_playlist_content(playlist_id, valid_media_ids)
            if success:
                logger.info(f"✅ Successfully updated playlist {playlist_name}")
            else:
                logger.error(f"❌ Failed to update playlist {playlist_name}")

if __name__ == "__main__":
    sync_playlists()
