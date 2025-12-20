"""
Mood-Based Auto-DJ Scheduler with Playtime Modes

Background task that runs every MOOD_CYCLE_SECONDS to:
1. Determine current playtime mode (Discovery/Refinement/LiveVote)
2. Select appropriate tracks based on mode
3. Queue them in AzuraCast

Playtime Modes:
- DISCOVERY: Play untagged tracks for community tagging (default: 18:00-20:00)
- REFINEMENT: Play tagged tracks for rating/verification (default: 20:00-00:00)
- LIVE_VOTE: Real-time voting influences next track (default: 00:00-02:00)
- AUTO: System decides based on library state (fallback)

Feature Flags:
- FEATURE_MOOD_AUTODJ: Enable/disable this scheduler
- MOOD_CYCLE_SECONDS: Interval between queue decisions (default: 300)
"""

import os
import asyncio
import logging
import random
from datetime import datetime, time
from typing import Optional, Dict, Any, List
from enum import Enum

logger = logging.getLogger("MoodScheduler")

# ========== PLAYTIME MODES ==========
class PlaytimeMode(Enum):
    DISCOVERY = "discovery"      # Play untagged tracks for tagging
    REFINEMENT = "refinement"    # Play tagged tracks for further rating
    LIVE_VOTE = "live_vote"      # Real-time voting controls next track
    AUTO = "auto"                # System decides based on conditions

# Schedule: hour -> mode (24h format, local time)
PLAYTIME_SCHEDULE = {
    # Morning/Day: Auto mode
    6: PlaytimeMode.AUTO,
    12: PlaytimeMode.AUTO,
    # Early Evening: Discovery (find new vibes)
    18: PlaytimeMode.DISCOVERY,
    20: PlaytimeMode.REFINEMENT,
    # Late Night: Live Vote (party mode)
    22: PlaytimeMode.LIVE_VOTE,
    # After midnight: Back to refinement
    2: PlaytimeMode.REFINEMENT,
}

# Genre focus for Discovery mode (can be extended)
DISCOVERY_GENRES = ["Techno", "House", "Trance", "DeepHouse", "Minimal", "Disco"]

# Configuration from environment
FEATURE_MOOD_AUTODJ = os.getenv("FEATURE_MOOD_AUTODJ", "false").lower() == "true"
MOOD_CYCLE_SECONDS = int(os.getenv("MOOD_CYCLE_SECONDS", "300"))
AZURACAST_URL = os.getenv("AZURACAST_URL", "http://192.168.178.210")
AZURACAST_API_KEY = os.getenv("AZURACAST_API_KEY")
STATION_ID = 1

# Current state
current_mode = PlaytimeMode.AUTO

def get_current_playtime_mode() -> PlaytimeMode:
    """Determine current playtime mode based on schedule."""
    now = datetime.now()
    current_hour = now.hour
    
    # Find the most recent schedule entry
    active_mode = PlaytimeMode.AUTO
    for hour, mode in sorted(PLAYTIME_SCHEDULE.items()):
        if current_hour >= hour:
            active_mode = mode
    
    # Handle wrap-around (after midnight but before first schedule entry)
    if current_hour < min(PLAYTIME_SCHEDULE.keys()):
        # Use the last entry from previous day
        active_mode = PLAYTIME_SCHEDULE[max(PLAYTIME_SCHEDULE.keys())]
    
    return active_mode

# Prometheus metrics (optional)
try:
    from prometheus_client import Counter, Gauge
    MOOD_QUEUE_TRIGGERED = Counter(
        'mood_queue_triggered_total',
        'Number of times a mood-based track was queued'
    )
    MOOD_FALLBACK_TRIGGERED = Counter(
        'mood_fallback_triggered_total', 
        'Number of times fallback rotation was used'
    )
    CURRENT_MODE_GAUGE = Gauge(
        'playtime_mode',
        'Current playtime mode (0=auto, 1=discovery, 2=refinement, 3=live_vote)'
    )
except ImportError:
    # Prometheus not installed - use dummy counters
    class DummyCounter:
        def inc(self): pass
        def set(self, v): pass
    MOOD_QUEUE_TRIGGERED = DummyCounter()
    MOOD_FALLBACK_TRIGGERED = DummyCounter()
    CURRENT_MODE_GAUGE = DummyCounter()


# ========== MODE-SPECIFIC TRACK SELECTION ==========

async def select_discovery_track(mongo_client) -> Optional[Dict[str, Any]]:
    """
    DISCOVERY MODE: Select an untagged/low-vote track for community tagging.
    
    Prioritizes:
    1. Tracks with 0 mood votes
    2. Tracks from DISCOVERY_GENRES
    3. Recently added tracks
    
    Returns:
        Track dict ready for queueing
    """
    try:
        # Get tracks with no/few mood votes
        untagged = mongo_client.get_untagged_tracks(genres=DISCOVERY_GENRES, limit=50)
        
        if not untagged:
            logger.info("No untagged tracks found - trying all genres")
            untagged = mongo_client.get_untagged_tracks(limit=30)
        
        if not untagged:
            logger.warning("No tracks available for Discovery mode")
            return None
        
        selected = random.choice(untagged)
        logger.info(f"[DISCOVERY] Selected: {selected.get('metadata', {}).get('title', 'Unknown')}")
        return selected
        
    except Exception as e:
        logger.error(f"Discovery track selection error: {e}")
        return None


async def select_refinement_track(mongo_client) -> Optional[Dict[str, Any]]:
    """
    REFINEMENT MODE: Select a tagged track for community rating/verification.
    
    Prioritizes:
    1. Tracks with mood tags but low vote count (needs more data)
    2. Controversial tracks (high variance in votes)
    
    Returns:
        Track dict ready for queueing
    """
    try:
        # Get tracks that have some tags but need more verification
        needs_refinement = mongo_client.get_tracks_needing_refinement(
            min_votes=1, 
            max_votes=10,
            limit=30
        )
        
        if not needs_refinement:
            # Fallback: just get tagged tracks
            needs_refinement = mongo_client.get_tagged_tracks(limit=30)
        
        if not needs_refinement:
            logger.warning("No tracks available for Refinement mode")
            return None
        
        selected = random.choice(needs_refinement)
        logger.info(f"[REFINEMENT] Selected: {selected.get('metadata', {}).get('title', 'Unknown')}")
        return selected
        
    except Exception as e:
        logger.error(f"Refinement track selection error: {e}")
        return None


async def select_live_vote_track(mongo_client, azura_client) -> Optional[Dict[str, Any]]:
    """
    LIVE_VOTE MODE: Select track based on real-time community votes.
    
    The most recent mood_next votes determine the next track.
    
    Returns:
        Track dict ready for queueing
    """
    try:
        # Get the dominant next mood from recent votes
        dominant_mood = mongo_client.get_dominant_next_mood(time_window_minutes=5)  # Shorter window for live
        
        if not dominant_mood:
            logger.info("[LIVE_VOTE] No recent votes - using popular fallback")
            return await select_refinement_track(mongo_client)
        
        logger.info(f"[LIVE_VOTE] Community voted for: {dominant_mood}")
        return await select_next_track_by_mood(mongo_client, dominant_mood)
        
    except Exception as e:
        logger.error(f"Live vote track selection error: {e}")
        return None


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
    Single iteration of the mood queue worker with Playtime Mode support.
    
    Selects tracks based on current mode:
    - DISCOVERY: Untagged tracks for tagging
    - REFINEMENT: Tagged tracks for rating verification
    - LIVE_VOTE: Community vote-driven selection
    - AUTO: System decides based on conditions
    
    Returns:
        True if a track was successfully queued
    """
    global current_mode
    
    try:
        # 1. Determine current playtime mode
        current_mode = get_current_playtime_mode()
        logger.info(f"=== Playtime Mode: {current_mode.value.upper()} ===")
        
        # Update Prometheus gauge
        mode_map = {PlaytimeMode.AUTO: 0, PlaytimeMode.DISCOVERY: 1, 
                    PlaytimeMode.REFINEMENT: 2, PlaytimeMode.LIVE_VOTE: 3}
        CURRENT_MODE_GAUGE.set(mode_map.get(current_mode, 0))
        
        track = None
        
        # 2. Select track based on mode
        if current_mode == PlaytimeMode.DISCOVERY:
            track = await select_discovery_track(mongo_client)
        elif current_mode == PlaytimeMode.REFINEMENT:
            track = await select_refinement_track(mongo_client)
        elif current_mode == PlaytimeMode.LIVE_VOTE:
            track = await select_live_vote_track(mongo_client, azura_client)
        else:  # AUTO mode
            # Check if we have enough tagged tracks
            dominant_mood = mongo_client.get_dominant_next_mood(time_window_minutes=10)
            if dominant_mood:
                track = await select_next_track_by_mood(mongo_client, dominant_mood)
            else:
                # Mix discovery and refinement
                import random
                if random.random() < 0.3:  # 30% discovery, 70% refinement
                    track = await select_discovery_track(mongo_client)
                else:
                    track = await select_refinement_track(mongo_client)
        
        # 3. Fallback if no mode-specific track found
        if not track:
            logger.info("Mode selection failed - using general fallback")
            track = await get_fallback_track(mongo_client)
        
        if not track:
            logger.warning("No track available to queue")
            return False
        
        # 4. Queue in AzuraCast
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
