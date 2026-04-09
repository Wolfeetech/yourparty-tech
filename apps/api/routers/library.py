import os
import logging
import asyncio
from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from models.schemas import (
    ScanRequest, TagImproveRequest, OrganizeRequest, 
    AzuraCastSyncRequest, MongoConfigRequest
)
from state import state
from genre_organizer import GenreOrganizer
from azuracast_client import AzuraCastClient
from mongo_client import MongoDatabaseClient, MongoClient
from track_matcher import TrackMatcher
from track_matcher import TrackMatcher
from library_service import get_library_service
from auth import get_current_active_user, User
from fastapi import Depends

router = APIRouter()
logger = logging.getLogger(__name__)

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
        try:
            # Run the expensive scan in a worker thread so the event loop stays responsive.
            files = await asyncio.to_thread(state.scanner.scan_directory, path)
            all_files.extend(files)
        except Exception as exc:
            logger.exception(f"Scan failed for path '{path}'", exc_info=exc)

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


@router.post("/scan")
async def scan_library(
    request: ScanRequest, 
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    logger.info(f"Received scan request for path: '{request.path}' from {current_user.username}")
    
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

@router.get("/library")
async def get_library():
    return state.library

@router.post("/improve-tags")
async def improve_tags(request: TagImproveRequest, current_user: User = Depends(get_current_active_user)):
    # Find file in library
    file_entry = next((f for f in state.library if f['path'] == request.file_path), None)
    if not file_entry:
        raise HTTPException(status_code=404, detail="File not found in library")

    result = state.tag_improver.improve_tags(request.file_path)
    return result

@router.post("/organize")
async def organize_library(request: OrganizeRequest, current_user: User = Depends(get_current_active_user)):
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

@router.post("/azuracast/sync")
async def azuracast_sync(request: AzuraCastSyncRequest, current_user: User = Depends(get_current_active_user)):
    client = AzuraCastClient(request.base_url, request.api_key, request.station_id)
    return client.sync_media()

# MongoDB Endpoints

@router.post("/mongo/connect")
async def connect_mongo(request: MongoConfigRequest, current_user: User = Depends(get_current_active_user)):
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

@router.post("/mongo/sync/metadata")
async def sync_metadata_to_mongo(current_user: User = Depends(get_current_active_user)):
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

@router.get("/library/all")
async def get_all_library_tracks():
    """Get ALL tracks from database immediately (Single Source of Truth)."""
    if not state.library_service:
        raise HTTPException(status_code=400, detail="Library Service not initialized. Connect to MongoDB first.")
    
    tracks = await state.library_service.get_all_tracks()
    return {"tracks": tracks, "count": len(tracks)}

@router.post("/library/sync")
async def sync_library_directory(directory: str, background: bool = False, current_user: User = Depends(get_current_active_user)):
    """Sync a directory with the library database."""
    if not state.library_service:
        raise HTTPException(status_code=400, detail="Library Service not initialized")
    
    stats = await state.library_service.sync_directory(directory, background)
    return stats

@router.post("/library/cleanup")
async def cleanup_missing_tracks(current_user: User = Depends(get_current_active_user)):
    """Remove tracks from database where files no longer exist."""
    if not state.library_service:
        raise HTTPException(status_code=400, detail="Library Service not initialized")
    
    removed = await state.library_service.cleanup_missing_files()
    return {"removed": removed}

@router.post("/library/sync-ids")
async def sync_azuracast_ids(current_user: User = Depends(get_current_active_user)):
    """Fetch AzuraCast Media IDs and link them to MongoDB tracks."""
    if not state.library_service or not state.azura_client:
        raise HTTPException(status_code=400, detail="Services not initialized")
    
    result = await state.library_service.sync_azuracast_ids(state.azura_client)
    return result

@router.post("/library/playlists/sync")
async def sync_playlists():
    """
    Trigger manual sync of Mood Playlists to AzuraCast.
    Updates 'Starlight', 'Slow Burn', etc. based on rules.
    """
    if not hasattr(state, 'playlist_service') or not state.playlist_service:
         raise HTTPException(status_code=400, detail="Playlist Service not available (Check AzuraCast connection)")
    
    results = await state.playlist_service.sync_all_playlists()
    return {"results": results}
