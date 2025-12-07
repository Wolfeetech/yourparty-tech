import os
import logging
import asyncio
import httpx
import random
from datetime import datetime, timedelta
from pymongo import MongoClient

# Configuration
MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME", "root")
MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "4f5cd00532af49b5941d6f6385b2e0bf")
MONGO_HOST = os.getenv("MONGO_HOST", "192.168.178.222")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}"

AZURACAST_URL = os.getenv("AZURACAST_URL", "https://192.168.178.210")
AZURACAST_API_KEY = os.getenv("AZURACAST_API_KEY", "9199dc63da623190:c9f8c3a22e25932753dd3f4d57fa0d9c")
STATION_ID = os.getenv("AZURACAST_STATION_ID", "1")

logger = logging.getLogger("SmartScheduler")

def get_db():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return client["yourparty"]

def get_top_artists(min_rating=4.0, min_votes=2):
    """
    Find artists with high average ratings.
    """
    db = get_db()
    pipeline = [
        {"$group": {
            "_id": "$artist",
            "avgRating": {"$avg": "$rating"},
            "count": {"$sum": 1}
        }},
        {"$match": {
            "avgRating": {"$gte": min_rating},
            "count": {"$gte": min_votes},
            "_id": {"$ne": None} # valid artist
        }},
        {"$sort": {"avgRating": -1}}
    ]
    
    results = list(db.ratings.aggregate(pipeline))
    artists = [r["_id"] for r in results]
    logger.info(f"[SmartScheduler] Found {len(artists)} top artists: {artists[:5]}...")
    return artists

async def get_azuracast_media():
    """
    Fetch all media files from AzuraCast. 
    Note: In production with thousands of songs, this needs pagination loop.
    """
    url = f"{AZURACAST_URL}/api/station/{STATION_ID}/files"
    headers = {"Authorization": f"Bearer {AZURACAST_API_KEY}"}
    
    all_media = []
    
    async with httpx.AsyncClient(verify=False, timeout=30) as client:
        try:
            # Simple fetch for now, assuming manageable library size
            # For full implementation, handle pagination if AzuraCast requires it
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                return resp.json()
            else:
                logger.error(f"Failed to fetch media: {resp.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error fetching media: {e}")
            return []

async def find_unrated_candidates(top_artists):
    """
    Find unrated songs by top artists.
    """
    if not top_artists:
        return []

    # 1. Get all known rated songs from DB
    db = get_db()
    rated_ids = set(db.ratings.distinct("song_id"))
    
    # 2. Get AzuraCast Media
    files = await get_azuracast_media()
    if not files:
        return []
        
    candidates = []
    
    for f in files:
        # Check if file has metadata
        if not f.get("artist") or not f.get("title"):
            continue
            
        song_id = f.get("unique_id") # Check AzuraCast ID field
        if not song_id:
             # Fallback if unique_id is missing, use path hash or similar if needed
             # But AzuraCast usually provides unique_id or id
             song_id = f.get("id_string") or f.get("id")

        # Check if Artist is in Top Artists (fuzzy match?)
        # For now, exact string match (case insensitive optional)
        artist = f["artist"]
        if artist in top_artists:
            # Check if ALREADY rated
            if song_id not in rated_ids:
                candidates.append(f)

    logger.info(f"[SmartScheduler] Found {len(candidates)} unrated candidates.")
    return candidates

async def update_smart_playlist(candidates):
    """
    Update the 'Smart Discovery' playlist in AzuraCast.
    """
    PLAYLIST_NAME = "Smart Discovery - Top Artist Unrated"
    
    url = f"{AZURACAST_URL}/api/station/{STATION_ID}/playlists"
    headers = {"Authorization": f"Bearer {AZURACAST_API_KEY}"}

    async with httpx.AsyncClient(verify=False, timeout=30) as client:
        # 1. Find or Create Playlist
        playlist_id = None
        current_playlists = (await client.get(url, headers=headers)).json()
        
        for pl in current_playlists:
            if pl["name"] == PLAYLIST_NAME:
                playlist_id = pl["id"]
                break
        
        if not playlist_id:
            # Create
            payload = {
                "name": PLAYLIST_NAME,
                "is_enabled": True,
                "type": "default", # Standard rotation
                "weight": 6, # Slightly higher than default
                "include_in_requests": True
            }
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code == 200:
                playlist_id = resp.json()["id"]
                logger.info(f"Created playlist {PLAYLIST_NAME} (ID: {playlist_id})")
            else:
                logger.error("Failed to create playlist")
                return

        # 2. Add songs to playlist (AzuraCast usually links media TO playlist)
        # We iterate candidates and enable the playlist for them
        
        # Batching or individual? AzuraCast API allows updating media wrappers.
        # PUT /station/{station_id}/media/{media_id}
        
        count = 0
        for song in candidates:
             if count > 50: break # Limit batch
             
             media_id = song.get("unique_id")
             media_url = f"{AZURACAST_URL}/api/station/{STATION_ID}/media/{media_id}"
             
             # Fetch current details to preserve other playlists
             try:
                 details_resp = await client.get(media_url, headers=headers)
                 if details_resp.status_code != 200: continue
                 
                 details = details_resp.json()
                 
                 # Add our playlist ID
                 current_pl_ids = [p["id"] for p in details.get("playlists", [])]
                 if playlist_id not in current_pl_ids:
                     current_pl_ids.append(playlist_id)
                     details["playlists"] = current_pl_ids
                     
                     # Update
                     await client.put(media_url, json=details, headers=headers)
                     count += 1
             except Exception as e:
                 logger.error(f"Error updating media {media_id}: {e}")

        logger.info(f"[SmartScheduler] Added {count} songs to {PLAYLIST_NAME}")

async def task_loop():
    while True:
        try:
            await run_smart_rotation()
        except Exception as e:
            logger.error(f"Smart Rotation Loop Error: {e}")
        
        # Run every 60 minutes
        await asyncio.sleep(3600)

if __name__ == "__main__":
    # Test run
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_smart_rotation())
