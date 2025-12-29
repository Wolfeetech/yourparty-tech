import os
import logging
import asyncio
from dotenv import load_dotenv
from mongo_client import MongoDatabaseClient
from azuracast_client import AzuraCastClient

# Load Env
load_dotenv()

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EnrichRatings")

async def enrich_metadata():
    """
    Fetch all rated tracks from MongoDB that are missing metadata.
    Query AzuraCast History to find them.
    Update MongoDB with the found Titles/Artists.
    """
    logger.info("Starting Metadata Enrichment...")

    # 1. Connect to DB
    # Env vars should be loaded by the container environment
    db = MongoDatabaseClient(
        connection_string=os.getenv("MONGO_URI"),
        database_name=os.getenv("MONGO_DB", "yourparty") # Unified DB Name
    )

    # 2. Connect to AzuraCast
    ac_url = os.getenv("AZURACAST_URL", "https://radio.yourparty.tech")
    ac_key = os.getenv("AZURACAST_API_KEY", "")
    ac_station = int(os.getenv("AZURACAST_STATION_ID", "1"))
    
    if not ac_key:
        logger.warning("AZURACAST_API_KEY not set. Cannot fetch history.")
        return

    # Use context manager if possible or just instance
    # AzuraCastClient is now async
    client = AzuraCastClient(ac_url, ac_key, ac_station)

    # 3. Fetch History
    try:
        logger.info(f"Fetching History from {ac_url}...")
        now_playing_data = await client.get_now_playing()
        
        # Build Map: Song ID -> {title, artist, album}
        id_map = {}
        
        # Process Current
        np_song = now_playing_data.get('now_playing', {}).get('song', {})
        if np_song.get('id'):
            id_map[str(np_song['id'])] = np_song
            
        # Process History
        for item in now_playing_data.get('song_history', []):
            s = item.get('song', {})
            if s.get('id'):
                id_map[str(s['id'])] = s
                
        logger.info(f"Loaded {len(id_map)} songs from history.")
        
    except Exception as e:
        logger.error(f"Failed to fetch history: {e}")
        return

    # 4. Fetch DB Tracks
    tracks = db.get_all_rated_tracks(min_rating=0.0)
    logger.info(f"Checking {len(tracks)} tracks in DB...")

    updated_count = 0
    
    for t in tracks:
        song_id = t['song_id']
        current_meta = t.get('metadata', {})
        file_path = t.get('file_path')
        
        # Check if needs update
        needs_update = False
        if not current_meta.get('title') or current_meta.get('title') == 'Unknown Title':
            needs_update = True
        if not current_meta.get('artist') or current_meta.get('artist') == 'Unknown Artist':
            needs_update = True
            
        if needs_update and song_id in id_map:
            new_data = id_map[song_id]
            
            # Construct update payload
            clean_meta = {
                "title": new_data.get('title'),
                "artist": new_data.get('artist'),
                "album": new_data.get('album', ''),
                "art": new_data.get('art', '')
            }
            
            logger.info(f"Updating ID {song_id}: {clean_meta['artist']} - {clean_meta['title']}")
            
            if file_path:
                db.sync_track_metadata(file_path, clean_meta, song_id)
                updated_count += 1
            else:
                # Try update by song_id directly
                db.tracks_collection.update_one(
                    {"song_id": song_id},
                    {"$set": {
                        "metadata": clean_meta,
                        "last_updated": t.get('rating', {}).get('timestamp', '') # Keep existing or new
                    }},
                    upsert=True
                )
                updated_count += 1
    
    logger.info(f"Enrichment Complete. Updated {updated_count} tracks.")
    db.close()

if __name__ == "__main__":
    asyncio.run(enrich_metadata())
