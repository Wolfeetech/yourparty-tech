
import asyncio
import os
import logging
from typing import Dict, List
from backend.mongo_client import MongoDatabaseClient
from backend.azuracast_client import AzuraCastClient

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MoodSync")

# Configuration
AZURACAST_API_URL = os.getenv("AZURACAST_API_URL", "http://192.168.178.210")
AZURACAST_API_KEY = os.getenv("AZURACAST_API_KEY", "9199dc63da623190:c9f8c3a22e25932753dd3f4d57fa0d9c")
STATION_ID = 1

class MoodSyncer:
    def __init__(self):
        self.mongo = MongoDatabaseClient()
        self.azura = AzuraCastClient(AZURACAST_API_URL, AZURACAST_API_KEY, STATION_ID)

    async def sync_moods(self):
        logger.info("Starting Mood Sync...")
        
        # 1. Get All Mood Data from MongoDB
        moods_data = self.mongo.get_all_moods()
        # Structure: {"euphoric": [song_doc, song_doc], ...} (Wait, get_all_moods returns list of {tag, count, song_id})
        # Actually I need to map Tag -> List of Song Paths/Titles to find them in AzuraCast.
        
        # Let's inspect get_all_moods implementation or fetch raw.
        # get_all_moods aggregates. I might need a more direct query here.
        
        # Helper: Map Song ID (MongoDB) -> Song Info
        valid_tags = ["energetic", "chill", "groovy", "dark", "euphoric"]
        
        # Fetch all songs with non-empty tags
        tagged_songs = self.mongo.moods_collection.find({"tag": {"$in": valid_tags}})
        
        # Group by Mood
        mood_map: Dict[str, List[str]] = {tag: [] for tag in valid_tags}
        
        for record in tagged_songs:
            song_id = record.get("song_id")
            tag = record.get("tag")
            if song_id and tag in mood_map:
                # Get song details to find filename
                song = self.mongo.tracks_collection.find_one({"_id": song_id})
                if song and "file_path" in song:
                    mood_map[tag].append(song["file_path"])
                elif song and "title" in song:
                     # Fallback to title matching if path missing
                     mood_map[tag].append(song["title"])

        logger.info(f"Resolved Moods from DB: { {k: len(v) for k,v in mood_map.items()} }")

        # 2. Fetch Media from AzuraCast to Map Path/Title -> Media ID
        logger.info("Fetching AzuraCast Media Library...")
        ac_media = self.azura.get_station_media()
        # Create Lookup Map
        # media entry structure: { "id": 123, "path": "test.mp3", "text": "Artist - Title" }
        media_lookup = {}
        for m in ac_media:
            # Normalize keys
            media_lookup[m.get("path")] = m["id"]
            media_lookup[m.get("text")] = m["id"]
        
        logger.info(f"Loaded {len(media_lookup)} media items from AzuraCast.")

        # 3. Create/Update Playlists
        current_playlists = await self.azura.get_playlists()
        playlist_map = {p["name"]: p["id"] for p in current_playlists}

        for mood, items in mood_map.items():
            if not items:
                continue
                
            playlist_name = f"Vibe: {mood.capitalize()}"
            playlist_id = playlist_map.get(playlist_name)
            
            # Create if missing
            if not playlist_id:
                logger.info(f"Creating Playlist: {playlist_name}")
                new_pl = self.azura.create_playlist(playlist_name)
                if new_pl:
                    playlist_id = new_pl["id"]
                else:
                    logger.error(f"Failed to create playlist {playlist_name}")
                    continue
            
            # Map Items to IDs
            media_ids = []
            for item in items:
                mid = media_lookup.get(item)
                # Try partial match if direct fail?
                if not mid:
                     # Simple fuzzy check
                    for path, id_val in media_lookup.items():
                        if item in path or path in item:
                            mid = id_val
                            break
                
                if mid:
                    media_ids.append(mid)
            
            if media_ids:
                # Update Playlist
                logger.info(f"Updating Playlist '{playlist_name}' with {len(media_ids)} tracks.")
                self.azura.replace_playlist_content(playlist_id, list(set(media_ids)))
            else:
                logger.warning(f"No media IDs found for mood {mood} (Source items: {len(items)})")

if __name__ == "__main__":
    syncer = MoodSyncer()
    asyncio.run(syncer.sync_moods())
