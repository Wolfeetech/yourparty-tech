"""
Central Library Service - Single Source of Truth

This is the core of the music library management system.
MongoDB is the primary source, filesystem is just storage.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import hashlib

from mongo_client import MongoDatabaseClient
from music_scanner import MusicScanner
from tag_improver import TagImprover

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LibraryService:
    """
    Central Library Service - Manages the entire music library.
    
    Responsibilities:
    - Single source of truth (MongoDB)
    - Background filesystem sync
    - Duplicate detection & merging
    - Metadata enrichment
    """
    
    def __init__(self, mongo_client: MongoDatabaseClient):
        self.mongo = mongo_client
        self.scanner = MusicScanner()
        self.tag_improver = TagImprover()
        self.sync_in_progress = False
    
    async def get_all_tracks(self) -> List[Dict[str, Any]]:
        """
        Get all tracks from database (primary source).
        This is what the UI should display immediately.
        
        Returns:
            List of all tracks with metadata and ratings
        """
        try:
            tracks = list(self.mongo.tracks_collection.find())
            
            # Enrich with ratings
            for track in tracks:
                if 'song_id' in track:
                    rating = self.mongo.get_track_rating(song_id=track['song_id'])
                    track['rating'] = rating
                
                # Convert ObjectId to string for JSON
                track['_id'] = str(track['_id'])
            
            logger.info(f"Loaded {len(tracks)} tracks from database")
            return tracks
            
        except Exception as e:
            logger.error(f"Error loading tracks: {e}")
            return []
    
    def generate_acoustic_fingerprint(self, file_path: str) -> Optional[str]:
        """
        Generate acoustic fingerprint using fpcalc (Chromaprint).
        This is the BEST way to detect duplicates.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Acoustic fingerprint hash or None
        """
        try:
            import acoustid
            duration, fingerprint = acoustid.fingerprint_file(file_path)
            # Use hash of fingerprint for storage
            return hashlib.sha256(fingerprint.encode()).hexdigest()
        except Exception as e:
            logger.warning(f"Could not generate fingerprint for {file_path}: {e}")
            return None
    
    def generate_metadata_fingerprint(self, metadata: Dict[str, Any]) -> str:
        """
        Generate metadata-based fingerprint (fallback).
        
        Args:
            metadata: Track metadata
            
        Returns:
            MD5 hash of artist+title+album
        """
        data = f"{metadata.get('artist', '')}|{metadata.get('title', '')}|{metadata.get('album', '')}"
        return hashlib.md5(data.lower().encode()).hexdigest()
    
    def find_duplicate(self, file_path: str, metadata: Dict[str, Any], acoustic_fp: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Find duplicate track in database using multiple strategies.
        
        Priority:
        1. Acoustic fingerprint (best)
        2. Metadata fingerprint
        3. Artist + Title match
        
        Args:
            file_path: File path
            metadata: Track metadata
            acoustic_fp: Optional acoustic fingerprint
            
        Returns:
            Duplicate track or None
        """
        # 1. Acoustic fingerprint (most reliable)
        if acoustic_fp:
            dup = self.mongo.tracks_collection.find_one({"acoustic_fingerprint": acoustic_fp})
            if dup:
                logger.info(f"Found duplicate by acoustic fingerprint: {metadata.get('title')}")
                return dup
        
        # 2. Metadata fingerprint
        meta_fp = self.generate_metadata_fingerprint(metadata)
        dup = self.mongo.tracks_collection.find_one({"metadata_fingerprint": meta_fp})
        if dup:
            logger.info(f"Found duplicate by metadata fingerprint: {metadata.get('title')}")
            return dup
        
        # 3. Artist + Title (fuzzy)
        if metadata.get('title') and metadata.get('artist'):
            dup = self.mongo.tracks_collection.find_one({
                "metadata.title": metadata['title'],
                "metadata.artist": metadata['artist']
            })
            if dup:
                logger.info(f"Found potential duplicate by title+artist: {metadata.get('title')}")
                return dup
        
        return None
    
    def merge_metadata(self, existing: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge metadata from two sources - keep the best quality.
        
        Priority:
        1. MusicBrainz data (most reliable)
        2. Existing data if better
        3. New data if better
        
        Args:
            existing: Existing metadata
            new: New metadata
            
        Returns:
            Merged metadata
        """
        merged = existing.copy()
        
        # For each field, keep the one with more information
        for key in ['title', 'artist', 'album', 'year', 'genre']:
            existing_val = existing.get(key, '')
            new_val = new.get(key, '')
            
            # Prefer non-empty, longer, more detailed
            if not existing_val or (new_val and len(str(new_val)) > len(str(existing_val))):
                merged[key] = new_val
        
        # Special: Genre - merge multiple
        if existing.get('genre') and new.get('genre'):
            existing_genres = set(str(existing['genre']).split(', '))
            new_genres = set(str(new['genre']).split(', '))
            merged['genre'] = ', '.join(sorted(existing_genres | new_genres))
        
        return merged
    
    async def add_or_update_track(self, file_path: str, metadata: Dict[str, Any], force_update: bool = False) -> Dict[str, str]:
        """
        Add new track or update existing (with deduplication).
        
        Args:
            file_path: Path to audio file
            metadata: Track metadata
            force_update: Force metadata update even if exists
            
        Returns:
            Result dict with action taken
        """
        try:
            # Check if file exists
            if not Path(file_path).exists():
                return {"action": "error", "reason": "file_not_found"}
            
            # Generate fingerprints
            acoustic_fp = self.generate_acoustic_fingerprint(file_path)
            metadata_fp = self.generate_metadata_fingerprint(metadata)
            
            # Find duplicate
            existing = self.find_duplicate(file_path, metadata, acoustic_fp)
            
            if existing:
                # Duplicate found - merge metadata
                merged_metadata = self.merge_metadata(existing.get('metadata', {}), metadata)
                
                # Update in database
                self.mongo.tracks_collection.update_one(
                    {"_id": existing["_id"]},
                    {"$set": {
                        "metadata": merged_metadata,
                        "metadata_fingerprint": metadata_fp,
                        "acoustic_fingerprint": acoustic_fp,
                        "last_updated": datetime.utcnow(),
                        "file_locations": list(set(existing.get("file_locations", []) + [file_path]))
                    }}
                )
                
                return {
                    "action": "merged",
                    "track_id": str(existing["_id"]),
                    "title": merged_metadata.get("title")
                }
            else:
                # New track - add to database
                track_doc = {
                    "file_path": file_path,
                    "file_locations": [file_path],
                    "metadata": metadata,
                    "metadata_fingerprint": metadata_fp,
                    "acoustic_fingerprint": acoustic_fp,
                    "added": datetime.utcnow(),
                    "last_updated": datetime.utcnow()
                }
                
                result = self.mongo.tracks_collection.insert_one(track_doc)
                
                return {
                    "action": "added",
                    "track_id": str(result.inserted_id),
                    "title": metadata.get("title")
                }
                
        except Exception as e:
            logger.error(f"Error adding/updating track {file_path}: {e}")
            return {"action": "error", "reason": str(e)}
    
    async def sync_directory(self, directory: str, background: bool = False) -> Dict[str, Any]:
        """
        Sync a directory with the database.
        
        This is the main sync operation:
        1. Scan directory for audio files
        2. Check each against database
        3. Add new, update existing, merge duplicates
        
        Args:
            directory: Directory to scan
            background: Run in background without blocking
            
        Returns:
            Sync statistics
        """
        if self.sync_in_progress and not background:
            return {"error": "Sync already in progress"}
        
        self.sync_in_progress = True
        stats = {
            "scanned": 0,
            "added": 0,
            "merged": 0,
            "updated": 0,
            "errors": 0
        }
        
        try:
            logger.info(f"Starting directory sync: {directory}")
            
            # Scan directory
            files = self.scanner.scan_directory(directory)
            stats["scanned"] = len(files)
            
            # Process each file
            for file_info in files:
                result = await self.add_or_update_track(
                    file_info['path'],
                    file_info['metadata']
                )
                
                if result["action"] == "added":
                    stats["added"] += 1
                elif result["action"] == "merged":
                    stats["merged"] += 1
                elif result["action"] == "error":
                    stats["errors"] += 1
            
            # Log sync operation
            self.mongo.log_sync_operation("directory_sync", {
                "directory": directory,
                "stats": stats
            })
            
            logger.info(f"Sync complete: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Sync error: {e}")
            return {"error": str(e)}
        finally:
            self.sync_in_progress = False
    
    async def cleanup_missing_files(self) -> int:
        """
        Remove tracks from database where all file locations are missing.
        
        Returns:
            Number of tracks removed
        """
        removed = 0
        
        try:
            tracks = list(self.mongo.tracks_collection.find())
            
            for track in tracks:
                file_locations = track.get("file_locations", [track.get("file_path")])
                
                # Check if ANY location still exists
                any_exists = any(Path(loc).exists() for loc in file_locations if loc)
                
                if not any_exists:
                    # No files found - remove from DB
                    self.mongo.tracks_collection.delete_one({"_id": track["_id"]})
                    removed += 1
                    logger.info(f"Removed missing track: {track.get('metadata', {}).get('title')}")
            
            return removed
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            return 0

# Global instance
_library_service = None

def get_library_service(mongo_client: MongoDatabaseClient) -> LibraryService:
    """Get or create global library service instance."""
    global _library_service
    if _library_service is None:
        _library_service = LibraryService(mongo_client)
    return _library_service
