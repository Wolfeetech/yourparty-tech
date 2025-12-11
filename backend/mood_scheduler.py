"""
Mood-Based Auto-DJ Scheduler

Background task that runs every MOOD_CYCLE_SECONDS to:
1. Analyze community mood votes
2. Select a track matching the dominant mood
3. Queue it in AzuraCast

Feature Flags:
- FEATURE_MOOD_AUTODJ: Enable/disable this scheduler
- MOOD_CYCLE_SECONDS: Interval between queue decisions (default: 300)
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger("MoodScheduler")

# Configuration from environment
FEATURE_MOOD_AUTODJ = os.getenv("FEATURE_MOOD_AUTODJ", "false").lower() == "true"
MOOD_CYCLE_SECONDS = int(os.getenv("MOOD_CYCLE_SECONDS", "300"))
AZURACAST_URL = os.getenv("AZURACAST_URL", "http://192.168.178.210")
AZURACAST_API_KEY = os.getenv("AZURACAST_API_KEY")
STATION_ID = 1

# Prometheus metrics (optional)
try:
    from prometheus_client import Counter
    MOOD_QUEUE_TRIGGERED = Counter(
        'mood_queue_triggered_total',
        'Number of times a mood-based track was queued'
    )
    MOOD_FALLBACK_TRIGGERED = Counter(
        'mood_fallback_triggered_total', 
        'Number of times fallback rotation was used'
    )
except ImportError:
    # Prometheus not installed - use dummy counters
    class DummyCounter:
        def inc(self): pass
    MOOD_QUEUE_TRIGGERED = DummyCounter()
    MOOD_FALLBACK_TRIGGERED = DummyCounter()


async def select_next_track_by_mood(mongo_client, dominant_mood: str) -> Optional[Dict[str, Any]]:
    """
    Select a track matching the dominant mood from the database.
    
    Args:
        mongo_client: MongoDatabaseClient instance
        dominant_mood: The mood to match
        
    Returns:
        Track dict with song_id and metadata, or None
    """
    if not mongo_client:
        logger.warning("MongoDB client not available")
        return None
    
    try:
        tracks = mongo_client.get_tracks_by_mood(dominant_mood, limit=20)
        
        if not tracks:
            logger.info(f"No tracks found for mood: {dominant_mood}")
            return None
        
        # Simple random selection from matching tracks
        import random
        selected = random.choice(tracks)
        
        logger.info(f"Selected track for mood '{dominant_mood}': {selected.get('metadata', {}).get('title', 'Unknown')}")
        return selected
        
    except Exception as e:
        logger.error(f"Error selecting track by mood: {e}")
        return None


async def queue_track_in_azuracast(azura_client, track: Dict[str, Any]) -> bool:
    """
    Queue a track in AzuraCast.
    
    Args:
        azura_client: AzuraCastClient instance
        track: Track dict with song_id
        
    Returns:
        True if successfully queued
    """
    try:
        song_id = track.get("song_id")
        if not song_id:
            logger.warning("Track has no song_id")
            return False
        
        # Add small delay to avoid hammering AzuraCast
        await asyncio.sleep(0.5)
        
        success = azura_client.queue_track(int(song_id))
        
        if success:
            logger.info(f"Successfully queued track: {track.get('metadata', {}).get('title', song_id)}")
            MOOD_QUEUE_TRIGGERED.inc()
        
        return success
        
    except Exception as e:
        logger.error(f"Error queuing track: {e}")
        return False


async def get_fallback_track(mongo_client) -> Optional[Dict[str, Any]]:
    """
    Get a random track from general rotation when mood selection fails.
    """
    try:
        # Get highly-rated tracks as fallback
        tracks = mongo_client.get_all_rated_tracks(min_rating=3.0)
        
        if not tracks:
            logger.warning("No fallback tracks available")
            return None
        
        import random
        selected = random.choice(tracks[:20])  # Top 20 rated
        
        MOOD_FALLBACK_TRIGGERED.inc()
        logger.info(f"Using fallback track: {selected.get('metadata', {}).get('title', 'Unknown')}")
        return selected
        
    except Exception as e:
        logger.error(f"Error getting fallback track: {e}")
        return None


async def mood_queue_worker_iteration(mongo_client, azura_client) -> bool:
    """
    Single iteration of the mood queue worker.
    
    Returns:
        True if a track was successfully queued
    """
    try:
        # 1. Get dominant mood from recent votes
        dominant_mood = mongo_client.get_dominant_next_mood(time_window_minutes=10)
        
        track = None
        
        if dominant_mood:
            logger.info(f"Dominant mood detected: {dominant_mood}")
            track = await select_next_track_by_mood(mongo_client, dominant_mood)
        else:
            logger.info("No dominant mood - using fallback")
        
        # 2. Fallback if no mood or no matching tracks
        if not track:
            track = await get_fallback_track(mongo_client)
        
        if not track:
            logger.warning("No track available to queue")
            return False
        
        # 3. Queue in AzuraCast
        success = await queue_track_in_azuracast(azura_client, track)
        
        return success
        
    except Exception as e:
        logger.error(f"Mood queue worker error: {e}")
        return False


async def schedule_mood_queue_worker(mongo_client, azura_client):
    """
    Background task that runs the mood queue worker on a cycle.
    
    This should be started as a background task from the main API.
    """
    logger.info(f"Mood Queue Worker starting (cycle: {MOOD_CYCLE_SECONDS}s, enabled: {FEATURE_MOOD_AUTODJ})")
    
    if not FEATURE_MOOD_AUTODJ:
        logger.info("FEATURE_MOOD_AUTODJ is disabled - worker will not run")
        return
    
    while True:
        try:
            logger.info("Running mood queue iteration...")
            await mood_queue_worker_iteration(mongo_client, azura_client)
            
        except Exception as e:
            logger.error(f"Mood queue worker error: {e}")
        
        # Wait for next cycle
        await asyncio.sleep(MOOD_CYCLE_SECONDS)


# For testing/manual execution
if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    
    from mongo_client import MongoDatabaseClient
    from azuracast_client import AzuraCastClient
    
    async def test_iteration():
        mongo = MongoDatabaseClient()
        azura = AzuraCastClient(AZURACAST_URL, AZURACAST_API_KEY or "", STATION_ID)
        
        result = await mood_queue_worker_iteration(mongo, azura)
        print(f"Queue result: {result}")
        
        mongo.close()
    
    asyncio.run(test_iteration())
