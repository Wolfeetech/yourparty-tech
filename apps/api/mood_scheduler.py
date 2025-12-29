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
from audio_science import CamelotWheel

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
AZURACAST_URL = os.getenv("AZURACAST_URL", "https://radio.yourparty.tech")
AZURACAST_API_KEY = os.getenv("AZURACAST_API_KEY")
STATION_ID = 1

# Time-Based Mood Curve (The Vibe)
# Hour -> Mood
MOOD_CURVE = {
    6: "energetic",    # Morning Energy
    12: "chill",       # Day Chill / Flow
    18: "euphoric",    # Evening Ramp-up
    21: "energetic",   # Prime Time
    3: "atmospheric"   # Late Night / Comedown
}

def get_curve_mood() -> Optional[str]:
    """Get the target mood based on the current time curve."""
    now = datetime.now()
    h = now.hour
    
    target = None
    # Find most recent scheduled mood
    for hour, mood in sorted(MOOD_CURVE.items()):
        if h >= hour:
            target = mood
            
    # Wrap around
    if not target:
        target = MOOD_CURVE[max(MOOD_CURVE.keys())]
    
    return target

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
        import inspect
        logger.info(f"DEBUG: mongo_client type: {type(mongo_client)}")
        logger.info(f"DEBUG: get_top_voted_track method: {mongo_client.get_top_voted_track}")
        try:
             logger.info(f"DEBUG: Sig: {inspect.signature(mongo_client.get_top_voted_track)}")
        except Exception as e:
             logger.info(f"DEBUG: Could not get sig: {e}")

        top_track_id = mongo_client.get_top_voted_track(time_window_minutes=5, station_id=station_id)
        
        if top_track_id:
             logger.info(f"[LIVE_VOTE] [STATION {station_id}] Winner by Track Vote: {top_track_id}")
             # Tracks are global, so we search by song_id only, preferring one with an AzuraCast ID
             track = mongo_client.tracks_collection.find_one({
                 "song_id": top_track_id,
                 "azuracast_id": {"$exists": True, "$ne": None}
             })
             if track:
                 return {
                    "song_id": top_track_id, 
                    "azuracast_id": track.get("azuracast_id"),
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


async def select_next_track_by_mood(mongo_client, dominant_mood: str, station_id: int = 1, current_key: str = None) -> Optional[Dict[str, Any]]:
    """
    Select a track matching the dominant mood from the database.
    Prioritizes Harmonic Mixing if current_key is provided.
    """
    if not mongo_client:
        logger.warning("MongoDB client not available")
        return None
    
    try:
        # 1. Try Harmonic Mixing first
        if current_key:
            compatible_keys = CamelotWheel.get_compatible_keys(current_key)
            if compatible_keys:
                logger.info(f"Harmonic Mixing: Looking for {dominant_mood} in keys {compatible_keys} (from {current_key})")
                harmonic_tracks = mongo_client.get_tracks_by_mood(
                    dominant_mood, 
                    limit=20, 
                    station_id=station_id,
                    allowed_keys=compatible_keys
                )
                if harmonic_tracks:
                    selected = random.choice(harmonic_tracks)
                    logger.info(f"HARMONIC MATCH! {selected.get('metadata', {}).get('title')} ({selected.get('metadata', {}).get('initial_key')})")
                    return selected
        
        # 2. Fallback to standard Mood selection
        tracks = mongo_client.get_tracks_by_mood(dominant_mood, limit=20, station_id=station_id)
        
        if not tracks:
            logger.info(f"No tracks found for mood '{dominant_mood}' on station {station_id}")
            return None
        
        selected = random.choice(tracks)
        logger.info(f"[STATION {station_id}] Selected track for mood '{dominant_mood}' (Non-Harmonic): {selected.get('metadata', {}).get('title', 'Unknown')}")
        return selected
        
    except Exception as e:
        logger.error(f"Error selecting track by mood for station {station_id}: {e}")
        return None


async def queue_track_in_azuracast(azura_client, track: Dict[str, Any], station_id: int = 1) -> bool:
    """
    Queue a track in AzuraCast.
    """
    try:
        # Try media_id first (numeric), fallback to song_id (hash string)
        media_id = track.get("azuracast_id") or track.get("media_id") or track.get("song_id")
        
        logger.info(f"DEBUG: Queueing -> Found IDs: azuracast_id={track.get('azuracast_id')}, song_id={track.get('song_id')}, Selected={media_id}")
        
        if not media_id:
            logger.warning("Track has no media_id or song_id")
            return False
        
        # Add small delay to avoid hammering AzuraCast
        await asyncio.sleep(0.5)
        
        # AzuraCast queue_track accepts both numeric ID and unique_id (hash)
        # Remove int() cast - song_id is a hash string
        success = await azura_client.queue_track(media_id, station_id=station_id)
        
        if success:
            logger.info(f"[STATION {station_id}] Successfully queued track: {track.get('metadata', {}).get('title', media_id)}")
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

        # Get Current Context (Key) for Harmonic Mixing
        current_key = None
        try:
            now_playing = await azura_client.get_now_playing(station_id=station_id)
            if now_playing and 'now_playing' in now_playing:
                current_song_id = now_playing['now_playing']['song']['id']
                # Look up in DB for Key
                # We need to find by AzuraCast ID (hash)
                # But our tracks might store media_id or unique_id as song_id? 
                # AzuraCast 'id' in 'song' object is the unique hash.
                
                # Check mapping. mongo_client.tracks usually stores 'song_id' as MD5 hash
                # AzuraCast.get_now_playing returns 'id' which is also hash.
                db_track = mongo_client.tracks_collection.find_one({"song_id": current_song_id})
                if not db_track:
                    # Try azuracast_id (numeric) if stored?
                    # But AzuraCast API often returns custom_fields too.
                    # Let's check custom_fields directly if available in API response?
                     pass
                     
                if db_track and 'metadata' in db_track:
                    current_key = db_track['metadata'].get('initial_key')
                    if current_key:
                        logger.info(f"[STATION {station_id}] Current Key: {current_key}")
                        
        except Exception as e:
            logger.warning(f"Failed to get current key context: {e}")

        # 0. Check Manual Override first
        track = None
        manual_target = None
        if current_steering and current_steering.get('mode') == 'manual':
             manual_target = current_steering.get('target')

        if manual_target:
            logger.info(f"=== [STATION {station_id}] MANUAL STEERING ACTIVE: {manual_target.upper()} ===")
            track = await select_next_track_by_mood(mongo_client, manual_target, station_id=station_id, current_key=current_key)

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
                # 1. User Votes (Dominant Mood)
                dominant_mood = mongo_client.get_dominant_next_mood(time_window_minutes=10, station_id=station_id)
                if dominant_mood:
                    logger.info(f"[AUTO] Using User Voted Mood: {dominant_mood}")
                    track = await select_next_track_by_mood(mongo_client, dominant_mood, station_id=station_id, current_key=current_key)
                
                # 2. The Vibe Curve (Time-based)
                if not track:
                    curve_mood = get_curve_mood()
                    if curve_mood:
                        logger.info(f"[AUTO] Using Vibe Curve Mood: {curve_mood}")
                        track = await select_next_track_by_mood(mongo_client, curve_mood, station_id=station_id, current_key=current_key)
                    
                # 3. Random Discovery/Refinement Fallback
                if not track:
                    if random.random() < 0.3:  # 30% discovery
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
