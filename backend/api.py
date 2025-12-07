import os
import logging
import asyncio
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from music_scanner import MusicScanner
from tag_improver import TagImprover
from genre_organizer import GenreOrganizer
from azuracast_client import AzuraCastClient
from mongo_client import MongoDatabaseClient
from track_matcher import TrackMatcher
from library_service import get_library_service

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Music Library Automation API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.post("/scan")
async def scan_library(request: ScanRequest):
    logger.info(f"Received scan request for path: '{request.path}'")
    
    # Support multiple paths separated by semicolon
    paths = [p.strip() for p in request.path.split(';') if p.strip()]
    
    all_files = []
    valid_paths = []

    for path in paths:
        # Fix common user typo: "C;/" -> "C:/" if it looks like a drive letter
        if len(path) >= 3 and path[1] == ';' and path[2] in ('/', '\\'):
             path = path[0] + ':' + path[2:]
        
        if not os.path.exists(path):
            logger.warning(f"Path does not exist: '{path}'")
            continue
        
        valid_paths.append(path)
        # Run scan
        files = state.scanner.scan_directory(path)
        all_files.extend(files)
    
    if not valid_paths:
        raise HTTPException(status_code=404, detail="No valid paths found")

    state.scan_path = request.path
    # Initialize organizer with the first valid path as default base
    if valid_paths:
        state.organizer = GenreOrganizer(valid_paths[0])
    
    state.library = all_files
    
    return {"count": len(all_files), "files": all_files[:100]}

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
