import asyncio
import logging
from typing import Dict, Any, List
from apps.api.mongo_client import MongoDatabaseClient
from apps.api.azuracast_client import AzuraCastClient
from apps.api.config_secrets import MONGO_URI, AZURACAST_API_URL, AZURACAST_API_KEY, AZURACAST_STATION_ID

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AzuraSync")

async def main():
    logger.info("Starting AzuraCast ID Sync...")
    
    # 1. Connect to MongoDB
    mongo = MongoDatabaseClient(MONGO_URI)
    
    # 2. Connect to AzuraCast
    # Note: Using base client which might be sync/async mixed. 
    # The `get_station_media` method uses requests (sync).
    azura = AzuraCastClient(AZURACAST_API_URL, AZURACAST_API_KEY, AZURACAST_STATION_ID)
    
    # 3. Fetch all media from AzuraCast
    logger.info("Fetching all media from AzuraCast... (this may take a moment)")
    try:
        # Paged response handling might be needed if library is huge
        # But `station/{id}/files` often returns strict list or paginated. 
        # Using the client we saw earlier, it does a simple get.
        media_response = azura.get_station_media()
        
        # Determine format (List or Paged)
        media_list = []
        if isinstance(media_response, list):
            media_list = media_response
        elif isinstance(media_response, dict):
             if 'rows' in media_response:
                 media_list = media_response['rows']
             else:
                 logger.warning(f"Response Keys: {media_response.keys()}")
                 # Try common keys
                 if 'files' in media_response: media_list = media_response['files']
                 elif 'media' in media_response: media_list = media_response['media']
        
        logger.info(f"Got {len(media_list)} tracks from AzuraCast.")
        
    except Exception as e:
        logger.error(f"Failed to fetch AzuraCast media: {e}")
        return

    # 4. Match and Update MongoDB
    matches = 0
    updates = 0
    
    for am_track in media_list:
        # Extract Identifiers
        ac_id = am_track.get('id')
        ac_unique_id = am_track.get('unique_id')
        ac_title = am_track.get('title', '').strip()
        ac_artist = am_track.get('artist', '').strip()
        ac_path = am_track.get('path', '') # Often relative like "Artist/Title.mp3"
        
        if not ac_id:
            continue
            
        # Strategy 1: Match by Path (Strongest)
        # AC Path: "Artist/Album/Song.mp3"
        # Local Path: "Z:\Artist\Album\Song.mp3"
        # We try to match the suffix.
        
        mongo_track = None
        
        # Try finding by path suffix
        # This is expensive in Mongo without regex index, but okay for batch job
        # Better: get all tracks and do in-memory match if library < 10k
        
        # Let's try direct query first
        if ac_artist and ac_title:
            mongo_track = mongo.tracks_collection.find_one({
                "metadata.title": ac_title,
                "metadata.artist": ac_artist
            })
            
        if not mongo_track:
             # Try simpler path match
             # No direct path match because paths differ (Z: vs /var/azuracast/...)
             pass
             
        if mongo_track:
            matches += 1
            
            # Check if needs update
            existing_ac_id = mongo_track.get('azuracast_id')
            if existing_ac_id != ac_id:
                mongo.tracks_collection.update_one(
                    {"_id": mongo_track["_id"]},
                    {"$set": {
                        "azuracast_id": ac_id,
                        "azuracast_unique_id": ac_unique_id,
                        "last_synced_azura": asyncio.get_event_loop().time()
                    }}
                )
                updates += 1
                if updates % 50 == 0:
                    logger.info(f"Updated {updates} tracks...")
    
    logger.info(f"Sync Complete. Matches: {matches}, Updates: {updates}")

if __name__ == "__main__":
    asyncio.run(main())
