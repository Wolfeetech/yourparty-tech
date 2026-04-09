import asyncio
import httpx
import random
import logging
import time
from datetime import datetime

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("StressTest")

# Configuration
API_URL = "http://localhost:8000"  # Running on CT 211
STATION_ID = 1
# A list of real song IDs (or we fetch them first)
KNOWN_TRACKS = []

async def fetch_listeners(client, listener_id):
    """Simulates a listener refreshing the page/player stats."""
    endpoints = [
        f"/nowplaying/{STATION_ID}", 
        f"/history/{STATION_ID}", 
        f"/station/{STATION_ID}/queue"
    ]
    while True:
        try:
            target = random.choice(endpoints)
            start = time.time()
            resp = await client.get(f"{API_URL}{target}")
            duration = time.time() - start
            if resp.status_code == 200:
                # logger.info(f"[Listener {listener_id}] {target} OK ({duration:.2f}s)")
                pass
            else:
                logger.error(f"[Listener {listener_id}] {target} FAILED: {resp.status_code}")
        except Exception as e:
            logger.error(f"[Listener {listener_id}] Error: {e}")
        
        await asyncio.sleep(random.uniform(5, 15))

async def fetch_curator_candidates(client):
    """Fetches a list of tracks to queue."""
    try:
        # Get random tracks from the library/rated endpoint
        resp = await client.get(f"{API_URL}/mongo/tracks/rated?min_rating=3.0&limit=50")
        if resp.status_code == 200:
            tracks = resp.json().get("tracks", [])
            return [t['song_id'] for t in tracks if 'song_id' in t]
    except Exception as e:
        logger.error(f"Failed to fetch candidates: {e}")
    return []

async def curator_action(client, curator_id):
    """Simulates a curator trying to queue music."""
    while True:
        try:
            # 1. Fetch Queue to see if full
            q_resp = await client.get(f"{API_URL}/station/{STATION_ID}/queue")
            queue = q_resp.json()
            
            if len(queue) > 5:
                logger.info(f"[Curator {curator_id}] Queue full ({len(queue)}), waiting...")
                await asyncio.sleep(60)
                continue

            # 2. Pick a track
            candidates = await fetch_curator_candidates(client)
            if not candidates:
                await asyncio.sleep(30)
                continue
                
            choice = random.choice(candidates)
            
            # 3. Queue it
            # Note: We are bypassing WP Auth here by hitting local FastAPI directly if allowed,
            # or we assume we are internal. The 'interactive' router might need `user` dependency.
            # If so, we might need to mock or use a backdoor. 
            # For this test, let's assume we use the /mongo/queue internal or similar if available,
            # OR we rely on the fact that we are running ON the server.
            
            # Actually, `interactive.py` endpoints like `/curator/queue` usually require auth.
            # But `azura_client.queue_track` can be called if we import the service code directly?
            # No, we want to test the API.
            
            # Let's try to hit the public /request endpoint if it exists, or the internal one.
            # If we struggle with Auth in this script, we'll verify read-load primarily
            # and use one 'Master' curator via Python code (not HTTP).
            
            pass 

        except Exception as e:
            logger.error(f"[Curator {curator_id}] Error: {e}")
            
        await asyncio.sleep(random.uniform(30, 120)) # Curators are slower

async def monitor_playback(client, target_song_id, target_title):
    """Watches for a specific song to play."""
    logger.info(f"👀 WATCHING FOR: {target_title} (ID: {target_song_id})")
    start_time = time.time()
    
    while True:
        try:
            resp = await client.get(f"{API_URL}/nowplaying/{STATION_ID}")
            data = resp.json()
            np = data.get("now_playing", {}).get("song", {})
            np_id = np.get("id")
            np_title = np.get("title")
            
            elapsed = time.time() - start_time
            
            if str(np_id) == str(target_song_id) or (target_title and target_title == np_title):
                logger.info(f"🎉 SUCCESS! Track '{target_title}' is NOW PLAYING after {elapsed/60:.1f} minutes!")
                return True
                
            # Logger beat every minute
            if int(elapsed) % 60 == 0:
                logger.info(f"   ... still waiting for '{target_title}'. Current: {np_title} (T+{elapsed/60:.1f}m)")
                
        except Exception as e:
            logger.error(f"Monitor error: {e}")
            
        await asyncio.sleep(10)

async def main():
    logger.info("🚀 STARTING FULL SYSTEM STRESS TEST")
    async with httpx.AsyncClient(timeout=30) as client:
        
        # 1. Start Listeners
        listeners = [asyncio.create_task(fetch_listeners(client, i)) for i in range(10)]
        logger.info(f"started {len(listeners)} listener agents.")
        
        # 2. Identify a track to queue "For Real"
        # We will use the internal code to queue it to ensure it gets in, 
        # then watch it via HTTP.
        
        # ... Wait for import ...
        from azuracast_client import AzuraCastClient
        from mongo_client import MongoDatabaseClient
        from state import state
        # Initialize clients manually since we are outside the app
        import os
        from dotenv import load_dotenv
        load_dotenv('.env')
        
        mongo = MongoDatabaseClient()
        azura = AzuraCastClient(
            os.getenv("AZURACAST_URL"), 
            os.getenv("AZURACAST_API_KEY"), 
            1
        )
        
        # Find a track
        candidates = mongo.get_all_rated_tracks(min_rating=4.5, limit=20)
        if not candidates:
            logger.error("No candidates found in DB!")
            return

        target_track = random.choice(candidates)
        t_id = target_track.get('azuracast_id') or target_track.get('song_id')
        t_title = target_track.get('metadata', {}).get('title', 'Unknown')
        
        logger.info(f"🎯 TARGET ACQUIRED: {t_title} (ID: {t_id})")
        
        # Queue it
        queued = await azura.queue_track(t_id, station_id=1)
        if queued:
            logger.info("✅ Target Track successfully queued in AzuraCast.")
        else:
            logger.error("❌ Failed to queue target track. Test Aborted.")
            return

        # 3. Start Monitor
        monitor = asyncio.create_task(monitor_playback(client, t_id, t_title))
        
        # 4. Run until monitor completes
        # We let the listeners hammer the API while we wait
        await monitor
        
        # Cleanup
        for t in listeners: t.cancel()

if __name__ == "__main__":
    import sys
    import os
    # Add path to find modules
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
    sys.path.append("/opt/radio-api/apps/api") # fallback for server path
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
