"""
Track Matching & Rating Protection System

This module ensures that ratings are preserved when tracks are moved/organized.
"""

import logging
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def generate_track_fingerprint(metadata: Dict[str, Any]) -> str:
    """
    Generate a unique fingerprint for a track based on metadata.
    This is used to match tracks even after they've been moved.
    
    Args:
        metadata: Track metadata dict
        
    Returns:
        MD5 hash fingerprint
    """
    # Use artist + title + album as unique identifier
    # (more reliable than file path which changes)
    fingerprint_data = f"{metadata.get('artist', '')}|{metadata.get('title', '')}|{metadata.get('album', '')}"
    return hashlib.md5(fingerprint_data.encode()).hexdigest()

def extract_song_id_from_path(file_path: str) -> Optional[str]:
    """
    Try to extract AzuraCast song ID from file path if it's stored in filename.
    Some systems store IDs in filenames like: "12345_songname.mp3"
    
    Args:
        file_path: Path to audio file
        
    Returns:
        Song ID if found, None otherwise
    """
    try:
        filename = Path(file_path).stem
        # Check if filename starts with digits followed by underscore
        if '_' in filename:
            potential_id = filename.split('_')[0]
            if potential_id.isdigit():
                return potential_id
    except Exception as e:
        logger.warning(f"Could not extract song ID from path {file_path}: {e}")
    
    return None

class TrackMatcher:
    """
    Matches local tracks with database records and AzuraCast songs.
    """
    
    def __init__(self, mongo_client=None):
        self.mongo_client = mongo_client
    
    def find_matching_track(self, file_path: str, metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find matching track in MongoDB by fingerprint or path.
        
        Args:
            file_path: Current file path
            metadata: Track metadata
            
        Returns:
            Matching track record with ratings, or None
        """
        if not self.mongo_client:
            return None
        
        try:
            # Method 1: Direct path match
            track = self.mongo_client.tracks_collection.find_one({"file_path": file_path})
            if track:
                logger.info(f"Found track by path: {file_path}")
                return track
            
            # Method 2: Metadata fingerprint match
            fingerprint = generate_track_fingerprint(metadata)
            track = self.mongo_client.tracks_collection.find_one({"metadata_fingerprint": fingerprint})
            if track:
                logger.info(f"Found track by fingerprint: {metadata.get('title')}")
                return track
            
            # Method 3: Title + Artist match (fuzzy)
            if metadata.get('title') and metadata.get('artist'):
                track = self.mongo_client.tracks_collection.find_one({
                    "metadata.title": metadata['title'],
                    "metadata.artist": metadata['artist']
                })
                if track:
                    logger.info(f"Found track by title+artist: {metadata['title']}")
                    return track
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding matching track: {e}")
            return None
    
    def preserve_ratings_on_move(self, old_path: str, new_path: str, metadata: Dict[str, Any]) -> bool:
        """
        Update track record when file is moved to preserve ratings.
        
        Args:
            old_path: Original file path
            new_path: New file path after organization
            metadata: Track metadata
            
        Returns:
            True if successful, False otherwise
        """
        if not self.mongo_client:
            return False
        
        try:
            # Find existing track
            existing = self.find_matching_track(old_path, metadata)
            
            if existing:
                # Update path while preserving song_id and ratings
                fingerprint = generate_track_fingerprint(metadata)
                
                self.mongo_client.tracks_collection.update_one(
                    {"_id": existing["_id"]},
                    {"$set": {
                        "file_path": new_path,
                        "metadata": metadata,
                        "metadata_fingerprint": fingerprint,
                        "previous_paths": existing.get("previous_paths", []) + [old_path]
                    }}
                )
                
                logger.info(f"Preserved ratings for: {metadata.get('title')} (moved to {new_path})")
                return True
            else:
                # Create new track record
                fingerprint = generate_track_fingerprint(metadata)
                self.mongo_client.sync_track_metadata(
                    new_path, 
                    metadata,
                    song_id=None
                )
                # Add fingerprint
                self.mongo_client.tracks_collection.update_one(
                    {"file_path": new_path},
                    {"$set": {"metadata_fingerprint": fingerprint}}
                )
                logger.info(f"Created new track record: {new_path}")
                return True
                
        except Exception as e:
            logger.error(f"Error preserving ratings: {e}")
            return False

if __name__ == "__main__":
    # Test fingerprinting
    test_metadata = {
        "artist": "Test Artist",
        "title": "Test Song",
        "album": "Test Album"
    }
    print(f"Fingerprint: {generate_track_fingerprint(test_metadata)}")
