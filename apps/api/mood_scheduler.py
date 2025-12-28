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

async def select_discovery_track(mongo_client, station_id: int = 1) -> Optional[Dict[str, Any]]:
    """
    DISCOVERY MODE: Select an untagged/low-vote track for community tagging.
    """
    try:
        # Get tracks with no/few mood votes for this station
        untagged = mongo_client.get_untagged_tracks(genres=DISCOVERY_GENRES, limit=50, station_id=station_id)
        
        if not untagged:
            logger.info(f"No untagged tracks found for station {station_id} - trying all genres")
            untagged = mongo_client.get_untagged_tracks(limit=30, station_id=station_id)
        
        if not untagged:
            logger.warning(f"No tracks available for Discovery mode on station {station_id}")
            return None
        
        selected = random.choice(untagged)
        logger.info(f"[DISCOVERY] [STATION {station_id}] Selected: {selected.get('metadata', {}).get('title', 'Unknown')}")
        return selected
        
    except Exception as e:
        logger.error(f"Discovery track selection error for station {station_id}: {e}")
        return None


async def select_refinement_track(mongo_client, station_id: int = 1) -> Optional[Dict[str, Any]]:
    """
    REFINEMENT MODE: Select a tagged track for community rating/verification.
    """
    try:
        # Get tracks that have some tags but need more verification
        needs_refinement = mongo_client.get_tracks_needing_refinement(
            min_votes=1, 
            max_votes=10,
            limit=30,
            station_id=station_id
        )
        
        if not needs_refinement:
            # Fallback: just get tagged tracks
            needs_refinement = mongo_client.get_tagged_tracks(limit=30, station_id=station_id)
        
        if not needs_refinement:
            logger.warning(f"No tracks available for Refinement mode on station {station_id}")
            return None
        
        selected = random.choice(needs_refinement)
        logger.info(f"[REFINEMENT] [STATION {station_id}] Selected: {selected.get('metadata', {}).get('title', 'Unknown')}")
        return selected
        
    except Exception as e:
        logger.error(f"Refinement track selection error for station {station_id}: {e}")
        return None


async def select_live_vote_track(mongo_client, azura_client, station_id: int = 1) -> Optional[Dict[str, Any]]:
    """
    LIVE_VOTE MODE: Select track based on real-time community votes.
    """
    try:
        # 1. Check for specific track votes (User explicitly voted for a track)
        top_track_id = mongo_client.get_top_voted_track(time_window_minutes=5, station_id=station_id)
        
        if top_track_id:
             logger.info(f"[LIVE_VOTE] [STATION {station_id}] Winner by Track Vote: {top_track_id}")
             track = mongo_client.tracks_collection.find_one({"song_id": top_track_id, "station_id": station_id})
             if track:
                 return {
                    "song_id": top_track_id, 
                    "file_path": track.get("file_path"),
                    "metadata": track.get("metadata", {})
                 }

        # 2. Check for dominant mood (User voted for a mood)
        dominant_mood = mongo_client.get_dominant_next_mood(time_window_minutes=5, station_id=station_id)
        
        if not dominant_mood:
            logger.info(f"[LIVE_VOTE] [STATION {station_id}] No recent votes - using popular fallback")
            return await select_refinement_track(mongo_client, station_id=station_id)
        
        logger.info(f"[LIVE_VOTE] [STATION {station_id}] Community voted for Mood: {dominant_mood}")
        return await select_next_track_by_mood(mongo_client, dominant_mood, station_id=station_id)
        
    except Exception as e:
        logger.error(f"Live vote track selection error for station {station_id}: {e}")
        return None


async def select_next_track_by_mood(mongo_client, dominant_mood: str, station_id: int = 1) -> Optional[Dict[str, Any]]:
    """
    Select a track matching the dominant mood from the database.
    """
    if not mongo_client:
        logger.warning("MongoDB client not available")
        return None
    
    try:
        tracks = mongo_client.get_tracks_by_mood(dominant_mood, limit=20, station_id=station_id)
        
        if not tracks:
            logger.info(f"No tracks found for mood '{dominant_mood}' on station {station_id}")
            return None
        
        selected = random.choice(tracks)
        logger.info(f"[STATION {station_id}] Selected track for mood '{dominant_mood}': {selected.get('metadata', {}).get('title', 'Unknown')}")
        return selected
        
    except Exception as e:
        logger.error(f"Error selecting track by mood for station {station_id}: {e}")
        return None


async def queue_track_in_azuracast(azura_client, track: Dict[str, Any], station_id: int = 1) -> bool:
    """
    Queue a track in AzuraCast.
    """
    try:
        song_id = track.get("song_id")
        if not song_id:
            logger.warning("Track has no song_id")
            return False
        
        # Add small delay to avoid hammering AzuraCast
        await asyncio.sleep(0.5)
        
        success = await azura_client.queue_track(int(song_id), station_id=station_id)
        
        if success:
            logger.info(f"[STATION {station_id}] Successfully queued track: {track.get('metadata', {}).get('title', song_id)}")
            MOOD_QUEUE_TRIGGERED.inc()
        
        return success
        
    except Exception as e:
        logger.error(f"Error queuing track for station {station_id}: {e}")
        return False


async def get_fallback_track(mongo_client, station_id: int = 1) -> Optional[Dict[str, Any]]:
    """
    Get a random track from general rotation when mood selection fails.
    """
    try:
        # Get highly-rated tracks as fallback
        tracks = mongo_client.get_all_rated_tracks(min_rating=3.0, station_id=station_id)
        
        if not tracks:
            logger.warning(f"No fallback tracks available for station {station_id}")
            return None
        
        selected = random.choice(tracks[:20])  # Top 20 rated
        
        MOOD_FALLBACK_TRIGGERED.inc()
        logger.info(f"[STATION {station_id}] Using fallback track: {selected.get('metadata', {}).get('title', 'Unknown')}")
        return selected
        
    except Exception as e:
        logger.error(f"Error getting fallback track: {e}")
        return None


async def mood_queue_worker_iteration(mongo_client, azura_client, station_id: int = 1, current_steering: dict = None) -> bool:
    """
    Single iteration per station with Manual Override support.
    """
    try:
        # PRE-FLIGHT CHECK: Avoid double-queuing
        try:
            upcoming = await azura_client.get_upcoming_queue(station_id=station_id)
            if upcoming and len(upcoming) > 0:
                logger.info(f"[STATION {station_id}] Skipping Auto-DJ: Queue already has {len(upcoming)} track(s).")
                return True
        except Exception as e:
            logger.warning(f"[STATION {station_id}] Failed to check AzuraCast queue: {e}")

        # 0. Check Manual Override first
        track = None
        manual_target = None
        if current_steering and current_steering.get('mode') == 'manual':
             manual_target = current_steering.get('target')

        if manual_target:
            logger.info(f"=== [STATION {station_id}] MANUAL STEERING ACTIVE: {manual_target.upper()} ===")
            track = await select_next_track_by_mood(mongo_client, manual_target, station_id=station_id)

        # If no manual target or manual selection failed, verify standard mode
        if not track:
            # 1. Determine current playtime mode
            mode = get_current_playtime_mode()
            logger.info(f"=== [STATION {station_id}] Playtime Mode: {mode.value.upper()} ===")
        
            # 2. Select track based on mode
            if mode == PlaytimeMode.DISCOVERY:
                track = await select_discovery_track(mongo_client, station_id=station_id)
            elif mode == PlaytimeMode.REFINEMENT:
                track = await select_refinement_track(mongo_client, station_id=station_id)
            elif mode == PlaytimeMode.LIVE_VOTE:
                track = await select_live_vote_track(mongo_client, azura_client, station_id=station_id)
            else:  # AUTO mode
                dominant_mood = mongo_client.get_dominant_next_mood(time_window_minutes=10, station_id=station_id)
                if dominant_mood:
                    track = await select_next_track_by_mood(mongo_client, dominant_mood, station_id=station_id)
                else:
                    if random.random() < 0.3:  # 30% discovery, 70% refinement
                        track = await select_discovery_track(mongo_client, station_id=station_id)
                    else:
                        track = await select_refinement_track(mongo_client, station_id=station_id)
        
        # 3. Fallback if no mode-specific track found
        if not track:
            logger.info(f"[STATION {station_id}] Mode selection failed - using general fallback")
            track = await get_fallback_track(mongo_client, station_id=station_id)
        
        if not track:
            logger.warning(f"[STATION {station_id}] No track available to queue")
            return False
        
        # 4. Queue in AzuraCast
        return await queue_track_in_azuracast(azura_client, track, station_id=station_id)
        
    except Exception as e:
        logger.error(f"Mood queue worker error for station {station_id}: {e}")
        return False


async def schedule_mood_queue_worker(mongo_client, azura_client, steering_status_map: dict):
    """
    Background task that runs the mood queue worker for each station independently.
    """
    logger.info(f"Mood Queue Worker starting (cycle: {MOOD_CYCLE_SECONDS}s, enabled: {FEATURE_MOOD_AUTODJ})")
    
    if not FEATURE_MOOD_AUTODJ:
        logger.info("FEATURE_MOOD_AUTODJ is disabled - worker will not run")
        return
    
    stations = [1, 2] # TODO: get from config
    
    while True:
        try:
            for sid in stations:
                steering = steering_status_map.get(sid)
                await mood_queue_worker_iteration(mongo_client, azura_client, station_id=sid, current_steering=steering)
            
        except Exception as e:
            logger.error(f"Mood queue worker main loop error: {e}")
        
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
