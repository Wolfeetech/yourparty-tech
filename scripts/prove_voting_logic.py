import asyncio
import logging
import time
from datetime import datetime
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
from apps.api.azuracast_client import AzuraCastClient
from apps.api.config_secrets import AZURACAST_API_URL, AZURACAST_API_KEY, MONGO_URI
from apps.api import mongo_client
print(f"DEBUG: Loading MongoDatabaseClient from: {mongo_client.__file__}")
from apps.api.mongo_client import MongoDatabaseClient

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ProofOfConcept")

# Config
STATION_ID = 1

async def prove_voting_loop():
    logger.info("🧪 STARTING VOTING SYSTEM PROOF OF CONCEPT (LIVE API)...")
    
    # 1. Connect Dependencies
    client = MongoClient(MONGO_URI)
    db = client["yourparty"] # Matches mongo_client.py default
    tracks = db["tracks"]
    votes = db["next_track_votes"] # Correct collection for specific track votes
    
    azura = AzuraCastClient(AZURACAST_API_URL, AZURACAST_API_KEY, STATION_ID)
    
    # 2. Select a Valid Track from AzuraCast (Source of Truth)
    logger.info("📡 Fetching Now Playing from AzuraCast to find valid ID...")
    try:
        np_response = await azura._get(f"{azura.base_url}/api/nowplaying/{STATION_ID}")
    except Exception as e:
        logger.error(f"Failed to fetch now_playing: {e}")
        return

    valid_media = None
    if np_response:
         # Try history first (don't want to vote for current playing)
         for entry in np_response.get('song_history', []):
             if entry.get('song', {}).get('id'):
                 valid_media = entry['song']
                 break
         
         # Fallback to current song
         if not valid_media and np_response.get('now_playing', {}).get('song', {}).get('id'):
             valid_media = np_response['now_playing']['song']

    if not valid_media:
        logger.error("❌ No valid media info found in Now Playing!")
        return

    real_azura_id = valid_media['id'] # This should be the string hash or int ID
    real_title = valid_media.get('title', 'Unknown')
    unique_id = valid_media.get('unique_id') or str(real_azura_id) # The hash
    
    logger.info(f"✅ Found valid AzuraCast Media: {real_title} (ID: {real_azura_id}, Unique: {unique_id})")

    # Find this track in MongoDB
    # Note: AzuraCast 'id' is the unique_id (hash) usually in recent versions, or numeric 'id'
    # We check both
    test_track = tracks.find_one({"azuracast_id": real_azura_id})
    if not test_track:
         test_track = tracks.find_one({"song_id": unique_id})
    
    if not test_track:
        logger.warning(f"⚠️ Track {real_azura_id} not in MongoDB. Updating it for test...")
        # Create a temp track doc for the test
        test_track = {
            "song_id": unique_id,
            "azuracast_id": real_azura_id,
            "metadata": {"title": real_title},
            "file_path": f"test/path_{unique_id}.mp3",
            "relative_path": f"test/path_{unique_id}.mp3" # Ensure unique index compliance
        }
        # Upsert by song_id
        tracks.replace_one({"song_id": unique_id}, test_track, upsert=True)

    track_title = test_track['metadata']['title']
    azura_id = test_track['azuracast_id']
    song_id = test_track['song_id']
    
    logger.info(f"🎯 TARGET TRACK: {track_title} (ID: {azura_id})")
    
    # 3. Simulate User Vote
    logger.info(f"🗳️ Simulating User Vote for '{track_title}'...")
    
    # Clean previous votes to ensure we win
    votes.delete_many({"station_id": STATION_ID})
    
    # Insert new vote
    votes.insert_one({
        "candidate_song_id": song_id,
        "station_id": STATION_ID,
        "user_ip": "127.0.0.1",
        "timestamp": datetime.utcnow()
    })
    logger.info("✅ Vote Cast! (Inserted into MongoDB)")
    
    # DEBUG: Dump the votes
    all_votes = list(votes.find({"station_id": STATION_ID}))
    logger.info(f"DEBUG: Current Votes in DB: {all_votes}")

    # 4. Trigger Scheduler Logic
    logger.info("🤖 Triggering Mood Scheduler Logic...")
    from apps.api.mood_scheduler import select_live_vote_track, queue_track_in_azuracast
    
    # Fix: select_live_vote_track expects the wrapper, not raw pymongo
    from apps.api.mongo_client import MongoDatabaseClient
    wrapper = MongoDatabaseClient(MONGO_URI)
    
    selected_winner = await select_live_vote_track(wrapper, azura, STATION_ID)
    
    if not selected_winner:
        logger.error("❌ Scheduler did NOT select our target track! Proof Failed.")
        return

    winner_title = selected_winner['metadata'].get('title', 'Unknown')
    logger.info(f"🏆 Scheduler Selected Winner: {winner_title}")

    # Normalize IDs for comparison
    sched_id = str(selected_winner['song_id'])
    vote_id = str(song_id)

    logger.info(f"DEBUG: Comparing IDs -> Scheduler: {sched_id} ({type(selected_winner['song_id'])}) vs Vote: {vote_id} ({type(song_id)})")
    
    if sched_id != vote_id:
        logger.error("❌ Mismatch! Scheduler selected a different track than voted.")
        return

    # 5. Push to AzuraCast Queue (Real API)
    logger.info("🚀 Pushing to AzuraCast Queue...")
    success = await queue_track_in_azuracast(azura, selected_winner, STATION_ID)
    
    if success:
        logger.info("✅ Request sent to AzuraCast API successfully.")
        
        # 6. Verify it's actually in the queue
        await asyncio.sleep(2) # Wait for AzuraCast to process
        logger.info("👀 Verifying AzuraCast Queue...")
        
        try:
            queue_data = await azura._get(f"{azura.base_url}/api/station/{STATION_ID}/queue")
            
            is_in_queue = False
            if queue_data:
                for item in queue_data:
                    # Check song ID match (nested)
                    if str(item.get('song', {}).get('id')) == str(azura_id):
                        is_in_queue = True
                        break
            
            if is_in_queue:
                logger.info(f"🎉 SUCCESS! '{track_title}' is visible in AzuraCast Queue!")
                logger.info("PROOF OF CONCEPT: PASSED ✅")
            else:
                logger.warning("⚠️ Request sent, but track not yet visible in Queue (AutoDJ delay?). Check Control Panel.")
        except Exception as e:
             logger.error(f"Failed to verify queue: {e}")
            
    else:
        logger.error("❌ Failed to push to AzuraCast.")

if __name__ == "__main__":
    asyncio.run(prove_voting_loop())
