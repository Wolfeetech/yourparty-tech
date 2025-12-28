import asyncio
import logging
import time
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
    logger.info("🧪 STARTING VOTING SYSTEM PROOF OF CONCEPT...")
    
    # 1. Connect Dependencies
    client = MongoClient(MONGO_URI)
    db = client["yourparty"]
    tracks = db["tracks"]
    votes = db["mood_next_votes"] # Assuming this is where votes go
    
    azura = AzuraCastClient(AZURACAST_API_URL, AZURACAST_API_KEY, STATION_ID)
    
    # 2. Select a Random Track to Vote For
    # Find a track that definitely has an AzuraCast ID
    test_track = tracks.find_one({"azuracast_id": {"$ne": None}})
    
    if not test_track:
        logger.error("❌ No valid tracks found in DB to test with!")
        return

    track_title = test_track['metadata']['title']
    azura_id = test_track['azuracast_id']
    song_id = test_track['song_id']
    
    logger.info(f"🎯 TARGET TRACK: {track_title} (ID: {azura_id})")
    
    # 3. Simulate User Vote
    logger.info(f"🗳️ Simulating User Vote for '{track_title}'...")
    
    # Clean previous votes for this track to verify freshness
    votes.delete_many({"song_id": song_id})
    
    # Insert new vote
    votes.insert_one({
        "song_id": song_id,
        "station_id": STATION_ID,
        "user_ip": "127.0.0.1",
        "timestamp": time.time(), 
        "mood": "energetic" 
    })
    logger.info("✅ Vote Cast! (Inserted into MongoDB)")
    
    # 4. Trigger Scheduler Logic (Simulated)
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
    
    if selected_winner['song_id'] != song_id:
        logger.error("❌ Mismatch! Scheduler selected a different track than voted.")
        return

    # 5. Push to AzuraCast Queue
    logger.info("🚀 Pushing to AzuraCast Queue...")
    success = await queue_track_in_azuracast(azura, selected_winner, STATION_ID)
    
    if success:
        logger.info("✅ Request sent to AzuraCast API successfully.")
        
        # 6. Verify it's actually in the queue
        await asyncio.sleep(2) # Wait for AzuraCast to process
        logger.info("👀 Verifying AzuraCast Queue...")
        
        queue_data = await azura._get(f"{azura.base_url}/api/station/{STATION_ID}/queue")
        
        is_in_queue = False
        for item in queue_data:
             if str(item['song']['id']) == str(azura_id):
                 is_in_queue = True
                 break
        
        if is_in_queue:
            logger.info(f"🎉 SUCCESS! '{track_title}' is visible in AzuraCast Queue!")
            logger.info("PROOF OF CONCEPT: PASSED ✅")
        else:
            logger.warning("⚠️ Request sent, but track not yet visible in Queue (AutoDJ delay?). Check Control Panel.")
            
    else:
        logger.error("❌ Failed to push to AzuraCast.")

if __name__ == "__main__":
    asyncio.run(prove_voting_loop())
