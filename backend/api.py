import os
import logging
import asyncio
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, WebSocket, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx # NEW: For Public API Polling
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ========== FEATURE FLAGS ==========
FEATURE_MOOD_VOTES = os.getenv("FEATURE_MOOD_VOTES", "true").lower() == "true"
FEATURE_MOOD_SYNC = os.getenv("FEATURE_MOOD_SYNC", "false").lower() == "true"
FEATURE_MOOD_AUTODJ = os.getenv("FEATURE_MOOD_AUTODJ", "false").lower() == "true"
MOOD_CYCLE_SECONDS = int(os.getenv("MOOD_CYCLE_SECONDS", "300"))
MOOD_VOTE_COOLDOWN_MINUTES = int(os.getenv("MOOD_VOTE_COOLDOWN_MINUTES", "5"))

from music_scanner import MusicScanner
from tag_improver import TagImprover
from genre_organizer import GenreOrganizer
from azuracast_client import AzuraCastClient
from mongo_client import MongoDatabaseClient
from track_matcher import TrackMatcher
from track_matcher import TrackMatcher
from library_service import get_library_service
from tag_writer import write_metadata_to_file # NEW: Direct ID3 Writing

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Music Library Automation API")

@app.get("/debug/ping")
async def debug_ping():
    return {"status": "pong", "mongo": state.mongo_client is not None}

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourparty.tech",
        "https://www.yourparty.tech",
        "https://radio.yourparty.tech",
        "https://control.yourparty.tech",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



from datetime import datetime

# Global State (In-memory for simplicity)
class AppState:
    def __init__(self):
        self.library: List[Dict[str, Any]] = []
        self.scanner = MusicScanner()
        self.tag_improver = TagImprover()
        self.organizer = None # Initialized with scan path
        self.scan_path = ""
        # MongoDB client (optional, initialized on first use)
        self.mongo_client = None
        # Track matcher for rating preservation
        self.track_matcher = None
        # Library Service (Single Source of Truth)
        self.library_service = None
        
        # Playback initialization
        self.now_playing = {
            "title": "Station Online",
            "artist": "YourParty Radio",
            "album": "",
            "art": "https://radio.yourparty.tech/wp-content/uploads/2023/11/station_logo.png", # Fallback logo
            "id": "init",
            "duration": 0
        }
        self.steering_status = {"mode": "auto", "target": "neutral"}
        self.stream_url = "https://radio.yourparty.tech/radio.mp3" # Default mount

state = AppState()

# Models
class ScanRequest(BaseModel):
    path: str

class OrganizeRequest(BaseModel):
    dry_run: bool = True
    output_path: str = None # Optional SMB/Network path

class TagImproveRequest(BaseModel):
    file_path: str

class AzuraCastSyncRequest(BaseModel):
    base_url: str
    api_key: str
    station_id: int

class MongoConfigRequest(BaseModel):
    connection_string: str = "mongodb://localhost:27017/"
    database_name: str = "radio_ratings"

class RatingRequest(BaseModel):
    song_id: str
    rating: int  # 1-5
    user_id: str = "anonymous"
    file_path: str = None

# Endpoints

@app.get("/")
async def root():
    return {"message": "Music Library Automation API is running"}

    return {"count": len(all_files), "files": all_files[:100]}

async def run_scan_background(paths: List[str]):
    """Background task to run the scan without blocking the main thread."""
    logger.info("Starting background scan...")
    all_files = []
    valid_paths = []
    
    for path in paths:
        if not os.path.exists(path):
            logger.warning(f"Path does not exist: '{path}'")
            continue
        valid_paths.append(path)
        # Assuming scanner.scan_directory is synchronous/CPU bound:
        # In a real prod env, run this in a threadpool:
        # await asyncio.to_thread(state.scanner.scan_directory, path)
        files = state.scanner.scan_directory(path) 
        all_files.extend(files)
    
    if valid_paths:
        state.scan_path = ";".join(valid_paths)
        state.organizer = GenreOrganizer(valid_paths[0])
        state.library = all_files
        logger.info(f"Background scan completed. Found {len(all_files)} files.")
        
        # Auto-Sync to MongoDB if connected
        if state.mongo_client:
            logger.info("Auto-syncing scan results to MongoDB...")
            synced = 0
            for file_entry in all_files:
                state.mongo_client.sync_track_metadata(file_entry['path'], file_entry['metadata'])
                synced += 1
            logger.info(f"Synced {synced} tracks to MongoDB.")


@app.post("/scan")
async def scan_library(request: ScanRequest, background_tasks: BackgroundTasks):
    logger.info(f"Received scan request for path: '{request.path}'")
    
    # Support multiple paths separated by semicolon
    paths = [p.strip() for p in request.path.split(';') if p.strip()]
    processed_paths = []

    for path in paths:
        # Fix common user typo: "C;/" -> "C:/"
        if len(path) >= 3 and path[1] == ';' and path[2] in ('/', '\\'):
             path = path[0] + ':' + path[2:]
        processed_paths.append(path)
    
    # Trigger background task
    background_tasks.add_task(run_scan_background, processed_paths)
    
    return {"message": "Scan started in background", "paths": processed_paths}

@app.get("/library")
async def get_library():
    return state.library

@app.post("/improve-tags")
async def improve_tags(request: TagImproveRequest):
    # Find file in library
    file_entry = next((f for f in state.library if f['path'] == request.file_path), None)
    if not file_entry:
        raise HTTPException(status_code=404, detail="File not found in library")

    result = state.tag_improver.improve_tags(request.file_path)
    
    if result['success']:
        # Update in-memory library
        # Note: This doesn't write to file yet, we need a separate 'apply' step or do it here
        # For this prototype, we just return the result
        pass
        
    return result

@app.post("/organize")
async def organize_library(request: OrganizeRequest):
    if not state.organizer:
        raise HTTPException(status_code=400, detail="Please scan a library first")
    
    results = []
    for file_entry in state.library:
        # Use current metadata from library state
        res = state.organizer.organize_file(
            file_entry['path'], 
            file_entry['metadata'], 
            dry_run=request.dry_run,
            output_path=request.output_path
        )
        results.append(res)
        
        # Update path in library if moved
        if res['success'] and not request.dry_run:
            old_path = file_entry['path']
            new_path = res['destination']
            file_entry['path'] = new_path
            
            # ⭐ PRESERVE RATINGS when file is moved
            if state.track_matcher and old_path != new_path:
                preserved = state.track_matcher.preserve_ratings_on_move(
                    old_path,
                    new_path,
                    file_entry['metadata']
                )
                if preserved:
                    logger.info(f"✅ Ratings preserved for: {file_entry['metadata'].get('title')}")
            
    return {"results": results}

@app.post("/azuracast/sync")
async def azuracast_sync(request: AzuraCastSyncRequest):
    client = AzuraCastClient(request.base_url, request.api_key, request.station_id)
    return client.sync_media()

# MongoDB Endpoints

@app.post("/mongo/connect")
async def connect_mongo(request: MongoConfigRequest):
    """Initialize MongoDB connection and Library Service."""
    try:
        state.mongo_client = MongoDatabaseClient(
            request.connection_string,
            request.database_name
        )
        # Initialize track matcher for rating preservation
        state.track_matcher = TrackMatcher(state.mongo_client)
        
        # ⭐ Initialize Library Service (Single Source of Truth)
        state.library_service = get_library_service(state.mongo_client)
        
        logger.info("MongoDB, TrackMatcher and LibraryService initialized")
        return {"success": True, "message": "MongoDB connected, Library Service ready"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mongo/rating/submit")
async def submit_rating(request: RatingRequest):
    """Submit a rating for a track."""
    if not state.mongo_client:
        raise HTTPException(status_code=400, detail="MongoDB not connected. Call /mongo/connect first.")
    
    result = state.mongo_client.submit_rating(
        request.song_id,
        request.rating,
        request.user_id,
        request.file_path
    )
    
    # ⭐ NEW: Immediate ID3 Write-Back
    # If file path is known, write the average rating to the file tags
    if request.file_path and os.path.exists(request.file_path):
        # We need the NEW average to write it perfectly
        new_stats = result.get("ratings", {})
        avg_rating = new_stats.get("average")
        if avg_rating:
            logger.info(f"Writing rating {avg_rating} to file tags: {request.file_path}")
            write_metadata_to_file(request.file_path, rating=avg_rating)
            
    return result

@app.get("/mongo/rating/{song_id}")
async def get_rating(song_id: str):
    """Get aggregated rating for a track."""
    if not state.mongo_client:
        raise HTTPException(status_code=400, detail="MongoDB not connected")
    
    rating = state.mongo_client.get_track_rating(song_id=song_id)
    if not rating:
        return {"average": 0, "total": 0, "distribution": {}}
    return rating

@app.get("/mongo/tracks/rated")
async def get_rated_tracks(min_rating: float = 0.0):
    """Get all tracks with ratings."""
    if not state.mongo_client:
        raise HTTPException(status_code=400, detail="MongoDB not connected")
    
    tracks = state.mongo_client.get_all_rated_tracks(min_rating)
    return {"tracks": tracks, "count": len(tracks)}

@app.post("/mongo/sync/metadata")
async def sync_metadata_to_mongo():
    """Sync current library metadata to MongoDB."""
    if not state.mongo_client:
        raise HTTPException(status_code=400, detail="MongoDB not connected")
    
    synced = 0
    for file_entry in state.library:
        state.mongo_client.sync_track_metadata(
            file_entry['path'],
            file_entry['metadata']
        )
        synced += 1
    
    
    state.mongo_client.log_sync_operation("metadata_sync", {
        "tracks_synced": synced
    })
    
    return {"success": True, "synced": synced}

# ⭐ NEW: Library Service Endpoints (Best Practice)

@app.get("/library/all")
async def get_all_library_tracks():
    """
    Get ALL tracks from database immediately (Single Source of Truth).
    This is what the UI should call on startup!
    
    Returns:
        All tracks with metadata and ratings
    """
    if not state.library_service:
        raise HTTPException(status_code=400, detail="Library Service not initialized. Connect to MongoDB first.")
    
    tracks = await state.library_service.get_all_tracks()
    return {"tracks": tracks, "count": len(tracks)}

@app.post("/library/sync")
async def sync_library_directory(directory: str, background: bool = False):
    """
    Sync a directory with the library database.
    
    This will:
    - Scan directory
    - Detect duplicates
    - Merge metadata
    - Add new tracks
    
    Args:
        directory: Directory to scan
        background: Run in background
        
    Returns:
        Sync statistics
    """
    if not state.library_service:
        raise HTTPException(status_code=400, detail="Library Service not initialized")
    
    stats = await state.library_service.sync_directory(directory, background)
    return stats

@app.post("/library/cleanup")
async def cleanup_missing_tracks():
    """
    Remove tracks from database where files no longer exist.
    
    Returns:
        Number of tracks removed
    """
    if not state.library_service:
        raise HTTPException(status_code=400, detail="Library Service not initialized")
    
    removed = await state.library_service.cleanup_missing_files()
    return {"removed": removed}

# --- REALTIME WEBSOCKET ---
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting: {e}")
                # clean up happens on disconnect

manager = ConnectionManager()

@app.websocket("/ws/logrmp")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    logger.info("New WebSocket connection established")
    try:
        # 1. Send immediate "Now Playing" (Mock or Real)
        # Check if we have library tracks
        current_track = {
            "title": "Deep Space Transmission",
            "artist": "YourParty Radio",
            "art": "https://placehold.co/600x600/10b981/ffffff?text=ON+AIR",
            "rating": {"average": 5.0}
        }
        
        if state.library:
            import random
            random_track = random.choice(state.library)
            current_track = {
                "title": random_track['metadata'].get('title', 'Unknown'),
                "artist": random_track['metadata'].get('artist', 'Unknown'),
                "art": "https://placehold.co/600x600/10b981/ffffff?text=Music", # Todo: Real Art URL
                "rating": {"average": 0.0} # Todo: Fetch real rating
            }
            
        await websocket.send_json({
            "type": "song",
            "data": current_track
        })

        # 2. Keep alive
        while True:
            # Wait for any message (ping/pong)
            data = await websocket.receive_text()
            # We could handle incoming 'vibe' votes here too
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket Error: {e}")
        # manager.disconnect(websocket) # Likely already closed


@app.on_event("startup")
async def startup_event():
    logger.info("Starting Radio API...")
    
    # Log feature flag status
    logger.info(f"Feature Flags: MOOD_VOTES={FEATURE_MOOD_VOTES}, MOOD_SYNC={FEATURE_MOOD_SYNC}, MOOD_AUTODJ={FEATURE_MOOD_AUTODJ}")
    
    # 1. Start Polling Loop IMMEDIATELY (Critical for UI)
    logger.info("Launching Public Status Loop...")
    asyncio.create_task(public_status_loop())

    # 2. Initialize Mongo (Can fail/timeout without blocking UI)
    try:
        from mongo_client import MongoDatabaseClient
        # Construct URI from individual vars if MONGO_URI is missing
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            user = os.getenv("MONGO_INITDB_ROOT_USERNAME", "root")
            pwd = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "")
            host = os.getenv("MONGO_HOST", "192.168.178.222")
            port = os.getenv("MONGO_PORT", "27017")
            if user and pwd:
                mongo_uri = f"mongodb://{user}:{pwd}@{host}:{port}/"
            else:
                mongo_uri = f"mongodb://{host}:{port}/"
        
        state.mongo_client = MongoDatabaseClient(mongo_uri)
        # Use simple timeout if possible, or just hope it doesn't hang forever
        await asyncio.wait_for(state.mongo_client.init(), timeout=5.0)
        logger.info("Connected to MongoDB.")
    except Exception as e:
        logger.error(f"Failed to connect to Mongo (Non-critical for Playback): {e}")

    # 3. Start Mood Auto-DJ Scheduler (if enabled)
    if FEATURE_MOOD_AUTODJ and state.mongo_client:
        try:
            from mood_scheduler import schedule_mood_queue_worker
            from azuracast_client import AzuraCastClient
            
            azura_url = os.getenv("AZURACAST_URL", "http://192.168.178.210")
            azura_key = os.getenv("AZURACAST_API_KEY", "")
            
            azura_client = AzuraCastClient(azura_url, azura_key, 1)
            
            logger.info(f"Starting Mood Auto-DJ (cycle: {MOOD_CYCLE_SECONDS}s)...")
            asyncio.create_task(schedule_mood_queue_worker(state.mongo_client, azura_client))
        except Exception as e:
            logger.error(f"Failed to start Mood Auto-DJ: {e}")

@app.get("/debug/status")
async def debug_status():
    """Debug endpoint to check internal state."""
    return {
        "now_playing": state.now_playing,
        "mongo_connected": state.mongo_client is not None,
        "loop_running": True # We assume it started if we are here
    }

@app.get("/status")
async def public_status():
    """Public status endpoint compatible with frontend polling."""
    return {
        "now_playing": {
            "song": state.now_playing
        },
        "listeners": {"total": 0}, 
        "playing_next": {"song": {"title": "Coming Soon", "artist": "YourParty"}},
        "steering": state.steering_status # Add steering info for dashboard/frontend
    }

@app.get("/queue")
async def get_queue():
    """Proxy AzuraCast Queue for Mission Control."""
    # We use a public endpoint or admin endpoint from AzuraCast
    # /api/station/{id}/queue
    url = f"{str(os.getenv('AZURACAST_URL', 'https://192.168.178.210'))}/api/station/1/queue"
    
    async with httpx.AsyncClient(verify=False) as client:
        try:
             # This endpoint often requires API Key, let's try with headers
             headers = {"X-API-Key": os.getenv("AZURACAST_API_KEY", "")}
             resp = await client.get(url, headers=headers, timeout=5.0)
             if resp.status_code == 200:
                 return resp.json()
             else:
                 return []
        except Exception as e:
            logger.error(f"Queue fetch error: {e}")
            return []

async def public_status_loop():
    """Poll AzuraCast public API for Metadata."""
    logger.info("Public Status Loop Started.")
    while True:
        try:
            # Public Endpoint: No Key Needed
            url = "http://192.168.178.210/api/nowplaying/1" 
            
            async with httpx.AsyncClient(verify=False, follow_redirects=True) as client:
                # Try HTTP first
                try:
                    resp = await client.get(url, timeout=5.0)
                except httpx.ConnectError:
                    # Fallback to HTTPS
                    url = "https://192.168.178.210/api/nowplaying/1"
                    resp = await client.get(url, timeout=5.0)

                if resp.status_code == 200:
                    data = resp.json()
                    np = data.get('now_playing', {}).get('song', {})
                    
                    for mount in data.get('station', {}).get('mounts', []):
                         if mount.get('is_default'):
                             state.stream_url = mount.get('url')

                    current_track = {
                        "title": np.get('title', ''),
                        "artist": np.get('artist', ''),
                        "album": np.get('album', ''),
                        "art": np.get('art', '').replace('http://192.168.178.210', 'https://radio.yourparty.tech').replace('https://192.168.178.210', 'https://radio.yourparty.tech'), 
                        "id": str(np.get('id', '0')), 
                        "duration": np.get('duration', 0)
                    }

                    # Fallback logic if AzuraCast returns empty fields but has 'text'
                    if not current_track['title'] or not current_track['artist']:
                        full_text = np.get('text', '')
                        if ' - ' in full_text:
                            parts = full_text.split(' - ', 1)
                            if not current_track['artist']:
                                current_track['artist'] = parts[0]
                            if not current_track['title']:
                                current_track['title'] = parts[1]
                        elif full_text and not current_track['title']:
                             current_track['title'] = full_text
                    
                    # Final fallback
                    if not current_track['title']: current_track['title'] = 'Unknown Track'
                    if not current_track['artist']: current_track['artist'] = 'Unknown Artist'
                    
                    # Inject Mongo Data if connected
                    if state.mongo_client:
                         song_id = current_track['id']
                         # Fetch Rating
                         rating_data = state.mongo_client.get_track_rating(song_id=song_id)
                         if rating_data:
                              current_track['rating'] = rating_data
                         else:
                              current_track['rating'] = {"average": 0.0, "total": 0}
                              
                         # Fetch Mood
                         mood_data = state.mongo_client.get_song_moods(song_id)
                         if mood_data.get('top_mood'):
                              current_track['top_mood'] = mood_data['top_mood']
                         else:
                              current_track['top_mood'] = None

                    state.now_playing = current_track
                    logger.info(f"Polled Track: {current_track['title']}")
                    
                    # Broadcast to WS
                    await manager.broadcast({
                        "type": "song",
                        "song": current_track
                    })
        except Exception as e:
            logger.error(f"Polling Error: {e}")
            
        await asyncio.sleep(2.0) # Faster polling for more responsiveness

# --- MISSING ENDPOINTS IMPLEMENTATION ---

class RatingRequest(BaseModel):
    song_id: str
    rating: int
    user_id: str = "anonymous"
    file_path: Optional[str] = None
    title: Optional[str] = None
    artist: Optional[str] = None

@app.post("/rate")
async def rate_track(request: RatingRequest):
    """Handle rating submission from frontend."""
    logger.info(f"Received rating: {request.rating} for song {request.song_id}")
    
    if state.mongo_client:
        result = state.mongo_client.submit_rating(
            song_id=request.song_id,
            rating=request.rating,
            user_id=request.user_id,
            file_path=request.file_path
        )
        return result
    else:
        # Fallback if Mongo is not connected
        logger.warning("MongoDB not connected. Rating not saved.")
        return {
            "success": True,
            "ratings": {
                "average": float(request.rating),
                "total": 1,
                "warning": "Persistence unavailable"
            }
        }

class MoodRequest(BaseModel):
    song_id: str
    mood: Optional[str] = None
    genre: Optional[str] = None
    title: Optional[str] = None
    artist: Optional[str] = None

@app.post("/mood-tag")
async def tag_mood(request: MoodRequest):
    """Handle mood tagging from frontend."""
    logger.info(f"Received tag - Mood: {request.mood}, Genre: {request.genre} for song {request.song_id}")
    
    if state.mongo_client:
        return state.mongo_client.submit_mood(
            song_id=request.song_id, 
            mood=request.mood, 
            genre=request.genre
        )
    
    return {"success": True, "warning": "Mock Success - DB Missing"}

# ========== MOOD VOTING SYSTEM ==========
class MoodVoteRequest(BaseModel):
    """Request model for dual mood voting (current + next)."""
    song_id: str
    mood_current: Optional[str] = None  # What mood IS this song?
    mood_next: Optional[str] = None     # What mood do you WANT next?
    rating: Optional[int] = None        # 1-5 star rating
    vote: Optional[str] = None          # like/dislike
    user_id: str = "anonymous"

VALID_MOODS = [
    "energy", "chill", "groove", "dark", "euphoric",
    "melancholic", "hypnotic", "aggressive", "trippy", "warm"
]

@app.post("/vote-mood")
async def vote_mood(request: MoodVoteRequest):
    """
    Handle dual mood voting from frontend.
    
    - mood_current: User's perception of current song's mood
    - mood_next: User's preference for the next song's mood
    
    This data is used to:
    1. Update the song's mood aggregates
    2. Influence automatic DJ decisions (when FEATURE_MOOD_AUTODJ is enabled)
    """
    # Feature flag check
    if not FEATURE_MOOD_VOTES:
        raise HTTPException(status_code=503, detail="Mood voting is currently disabled")
    
    # Validate moods
    if request.mood_current and request.mood_current not in VALID_MOODS:
        raise HTTPException(status_code=400, detail=f"Invalid mood_current: {request.mood_current}")
    if request.mood_next and request.mood_next not in VALID_MOODS:
        raise HTTPException(status_code=400, detail=f"Invalid mood_next: {request.mood_next}")
    
    if not request.mood_current and not request.mood_next and not request.rating:
        raise HTTPException(status_code=400, detail="At least one of mood_current, mood_next, or rating required")
    
    logger.info(f"Mood vote: song={request.song_id}, current={request.mood_current}, next={request.mood_next}")
    
    result = {
        "success": True,
        "song_id": request.song_id,
        "mood_current": request.mood_current,
        "mood_next": request.mood_next
    }
    
    if state.mongo_client:
        # Store mood vote for current song perception
        if request.mood_current:
            state.mongo_client.submit_mood(
                song_id=request.song_id,
                mood=request.mood_current
            )
        
        # Store mood_next preference in a separate collection for DJ decisions
        if request.mood_next:
            state.mongo_client.submit_mood_next_vote(
                song_id=request.song_id,
                mood_next=request.mood_next,
                user_id=request.user_id
            )
        
        # Handle rating if provided
        if request.rating:
            state.mongo_client.submit_rating(
                song_id=request.song_id,
                rating=request.rating,
                user_id=request.user_id
            )
            result["rating"] = request.rating
        
        # Get updated aggregates
        mood_data = state.mongo_client.get_song_moods(request.song_id)
        result["mood_counts"] = mood_data.get("mood_counts", {})
        result["dominant_mood"] = mood_data.get("top_mood")
    else:
        result["warning"] = "Database not connected - vote not persisted"
    
    return result

@app.get("/mood-stats")
async def get_mood_stats():
    """Get aggregated mood statistics for the current time window."""
    if not state.mongo_client:
        return {"error": "Database not connected"}
    
    return {
        "dominant_next_mood": state.mongo_client.get_dominant_next_mood(time_window_minutes=10),
        "feature_flags": {
            "FEATURE_MOOD_VOTES": FEATURE_MOOD_VOTES,
            "FEATURE_MOOD_SYNC": FEATURE_MOOD_SYNC,
            "FEATURE_MOOD_AUTODJ": FEATURE_MOOD_AUTODJ,
            "MOOD_CYCLE_SECONDS": MOOD_CYCLE_SECONDS
        }
    }

@app.get("/history")
async def get_history():
    """Return recently played tracks."""
    # Mock history for now since we don't have a DB of history yet
    return [
        {"title": "Sandstorm", "artist": "Darude", "time": "12:00", "art": "https://placehold.co/100"},
        {"title": "Level", "artist": "Avicii", "time": "11:55", "art": "https://placehold.co/100"}
    ]

@app.get("/moods")
async def get_moods(song_id: Optional[str] = None):
    """Get moods. If song_id provided, for that song. Else all."""
    if not state.mongo_client:
         return {}

    if song_id:
        # Fetch real specific moods if implemented, or return empty
        return {} 
    
    return state.mongo_client.get_all_moods()

@app.get("/ratings")
async def get_ratings(song_id: Optional[str] = None):
    """Get ratings. If song_id provided, for that song. Else all."""
    if not state.mongo_client:
        return {}

    if song_id:
         return state.mongo_client.get_track_rating(song_id)

    # Return All for Dashboard
    tracks = state.mongo_client.get_all_rated_tracks()
    return {
        t['song_id']: {
            "average": t['rating']['average'], 
            "total": t['rating']['total'], 
            "title": t.get('metadata', {}).get('title', 'Unknown'), 
            "artist": t.get('metadata', {}).get('artist', 'Unknown'),
            "path": t.get('path', '')
        } 
        for t in tracks 
        if 'song_id' in t
    }

@app.get("/history")
async def get_history():
    """
    Get playback history.
    Currently returns recently rated tracks as a proxy.
    """
    if not state.mongo_client:
        return []
        
    # Get last 10 rated tracks as 'history'
    tracks = state.mongo_client.get_all_rated_tracks(min_rating=0.0)
    # Sort by 'added_at' or similar if available, or just take top
    
    history_items = []
    import time
    for t in tracks[:10]:
        history_items.append({
            "song": t,
            "played_at": time.time() - 3600 # Mock time relative to now is okay for display
        })
    return history_items

# --- STEERING CONTROL ---
class SteeringRequest(BaseModel):
    mode: str = "auto" # auto, mood
    target: Optional[str] = None # e.g. "energetic"

@app.get("/control/steer")
async def get_steering():
    """Get current steering status."""
    return state.steering_status

@app.post("/control/steer")
async def set_steering(request: SteeringRequest):
    """Set steering mode."""
    state.steering_status = {
        "mode": request.mode,
        "target": request.target,
        "updated_at": datetime.utcnow().isoformat()
    }
    logger.info(f"Steering updated: {state.steering_status}")
    return state.steering_status

class VoteNextRequest(BaseModel):
    vote: str # energetic, chill, etc.

@app.post("/vote-next")
async def vote_next(request: VoteNextRequest):
    """
    Vote for the next vibe.
    """
    # In a real app, store this in a 'VotingManager'
    logger.info(f"Received Vibe Vote: {request.vote}")
    
    # Simple persistence in-memory for now to show impact
    state.steering_status['target'] = request.vote
    state.steering_status['mode'] = 'manual'
    
    # Broadcast to all clients
    await manager.broadcast({
        "type": "vibe",
        "data": {
            "vote": request.vote,
            "trend": request.vote.upper(),
            "status": "Vibe Shift Detected!"
        }
    })
    
    # Also broadcast steering status update for dashboard
    await manager.broadcast({
        "type": "steering",
        "data": state.steering_status
    })
    
    return {"status": "accepted", "vote": request.vote, "trend": request.vote.upper(), "prediction": {"title": f"Upcoming {request.vote.capitalize()} Track"}}

@app.post("/tasks/recalc-playlists")
async def recalc_playlists_task(bg_tasks: BackgroundTasks):
    """
    Beta: Recalculate AzuraCast playlists based on ratings.
    """
    bg_tasks.add_task(run_playlist_sync)
    return {"status": "started"}

async def run_playlist_sync():
    logger.info("Starting Playlist Sync...")
    if not state.mongo_client:
        logger.error("Mongo not connected.")
        return

    # 1. Fetch Top Rated Tracks (> 4 stars)
    top_tracks = state.mongo_client.get_all_rated_tracks(min_rating=4.0)
    logger.info(f"Found {len(top_tracks)} top rated tracks.")

    if not top_tracks:
        return

    # 2. Connect to AzuraCast
    # Fallback credentials from investigation
    ac_url = os.getenv("AZURACAST_URL", "http://192.168.178.210") 
    ac_key = os.getenv("AZURACAST_API_KEY", "9199dc63da6223190:c9f8c3a22e25932753dd3f4d57fa0d9c")
    station_id = 1 

    client = AzuraCastClient(ac_url, ac_key, station_id)
    
    # 3. Ensure 'Top Rated' Playlist exists
    playlists = await client.get_playlists()
    target_pl = next((p for p in playlists if p['name'] == "Top Rated"), None)
    
    if not target_pl:
        logger.info("Creating 'Top Rated' playlist...")
        target_pl = client.create_playlist("Top Rated", weight=5)
    
    if not target_pl:
        logger.error("Could not create/find playlist.")
        return

    # 4. Map Mongo Tracks to AzuraCast Media IDs
    logger.info("Fetching AzuraCast Media Library for matching...")
    ac_media = client.get_station_media()
    
    # Check if ac_media is a list or dict wrapper (AzuraCast API varies)
    if isinstance(ac_media, dict) and 'files' in ac_media:
        # Some versions return pages, or a wrapper
        media_list = ac_media['files']
    elif isinstance(ac_media, list):
        media_list = ac_media
    else:
        logger.error(f"Unexpected AzuraCast media response: {type(ac_media)}")
        return

    logger.info(f"AzuraCast has {len(media_list)} files.")

    # Create a Lookup Map: Filename -> Media ID
    # We clean the paths to matched filenames
    media_map = {}
    for item in media_list:
        # Item usually has 'path', 'id', 'text', 'artist', 'title'
        # Path example: "Music/DeepHouse/song.mp3"
        f_path = item.get('path', '')
        f_name = os.path.basename(f_path) 
        media_map[f_name] = item.get('id')
    
    matched_ids = []
    matched_count = 0
    
    for t in top_tracks:
        # Mongo: /var/radio/music/library/Genre/Song.mp3
        m_path = t.get('path', '')
        m_name = os.path.basename(m_path)
        
        if m_name in media_map:
            matched_ids.append(media_map[m_name])
            matched_count += 1
        else:
            # logger.debug(f"Could not match Mongo track {m_name} to AzuraCast.")
            pass
            
    logger.info(f"Matched {matched_count} / {len(top_tracks)} tracks to AzuraCast Media IDs.")
    
    if matched_ids:
        # 5. Assign to Playlist
        success = client.replace_playlist_content(target_pl['id'], matched_ids)
        if success:
            logger.info("SUCCESS: 'Top Rated' Playlist updated in AzuraCast!")
            # Use socket manager if available to broadcast success?
        else:
            logger.error("FAILED to update AzuraCast playlist.")
    else:
        logger.warning("No tracks matched. Check file paths or naming.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
