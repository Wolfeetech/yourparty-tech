"""
Async ID3 Tagger Service
YourParty.tech V2 - DJ Portability Layer

Writes votes/ratings into actual ID3 tags for portability:
- POPM (Popularimeter): Rating compatible with Rekordbox/iTunes
- TXXX (User-defined): Mood tags
- COMM (Comment): Mood description

This ensures all metadata travels WITH the files,
making them compatible with:
- Rekordbox
- Serato
- Mixxx
- iTunes
- MediaMonkey
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from queue import Queue
from threading import Thread

logger = logging.getLogger("id3-tagger")

# Try to import mutagen
try:
    from mutagen.id3 import ID3, POPM, TXXX, COMM, TIT2, TPE1, TALB
    from mutagen.mp3 import MP3
    from mutagen.flac import FLAC
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False
    logger.warning("mutagen not installed - ID3 tagging disabled")


# Rekordbox/iTunes compatible email for POPM
POPM_EMAIL = "yourparty.tech"

# Mood to Unix comment mapping (for DJ software compatibility)
MOOD_DESCRIPTIONS = {
    "energy": "High Energy / Peak Time",
    "chill": "Chill / Downtempo",
    "dark": "Dark / Underground",
    "euphoric": "Euphoric / Uplifting",
    "atmospheric": "Atmospheric / Ambient",
    "groovy": "Groovy / Funk",
    "melancholic": "Melancholic / Emotional",
    "aggressive": "Aggressive / Hard"
}


class AsyncTaggerService:
    """
    Asynchronous ID3 tag writing service.
    
    Uses a background thread to write tags without blocking the API.
    Maintains a queue of pending tag operations.
    """
    
    def __init__(self, library_root: str = None):
        self.library_root = library_root or os.getenv(
            "LIBRARY_ROOT_LINUX",
            "/var/radio/music/yourparty_Libary"
        )
        self.enabled = MUTAGEN_AVAILABLE
        self.queue: Queue = Queue()
        self._worker_thread: Optional[Thread] = None
        self._running = False
        
        if self.enabled:
            self._start_worker()
    
    def _start_worker(self):
        """Start background worker thread"""
        self._running = True
        self._worker_thread = Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()
        logger.info("ID3 Tagger worker started")
    
    def _worker_loop(self):
        """Background worker that processes tag queue"""
        while self._running:
            try:
                # Wait for item with timeout
                try:
                    item = self.queue.get(timeout=1.0)
                except:
                    continue
                
                if item is None:
                    break
                
                # Process tag operation
                operation = item.get("operation")
                if operation == "rating":
                    self._write_rating(
                        item["file_path"],
                        item["rating"],
                        item.get("play_count", 0)
                    )
                elif operation == "mood":
                    self._write_mood(
                        item["file_path"],
                        item["mood"]
                    )
                elif operation == "full":
                    self._write_full_metadata(
                        item["file_path"],
                        item.get("rating"),
                        item.get("mood"),
                        item.get("metadata", {})
                    )
                
                self.queue.task_done()
                
            except Exception as e:
                logger.error(f"Tagger worker error: {e}")
    
    def stop(self):
        """Stop the background worker"""
        self._running = False
        self.queue.put(None)  # Poison pill
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
    
    # ========================================
    # PUBLIC API (Async, Non-blocking)
    # ========================================
    
    async def queue_rating(
        self,
        file_path: str,
        rating: float,
        play_count: int = 0
    ) -> bool:
        """
        Queue a rating to be written to ID3 tags.
        
        Args:
            file_path: Path to audio file
            rating: Rating value (0-5 scale)
            play_count: Optional play count for POPM
        """
        if not self.enabled:
            return False
        
        resolved_path = self._resolve_path(file_path)
        if not resolved_path:
            return False
        
        self.queue.put({
            "operation": "rating",
            "file_path": resolved_path,
            "rating": rating,
            "play_count": play_count
        })
        return True
    
    async def queue_mood(
        self,
        file_path: str,
        mood: str
    ) -> bool:
        """
        Queue a mood tag to be written.
        
        Args:
            file_path: Path to audio file
            mood: Mood identifier (e.g., "energy", "chill")
        """
        if not self.enabled:
            return False
        
        resolved_path = self._resolve_path(file_path)
        if not resolved_path:
            return False
        
        self.queue.put({
            "operation": "mood",
            "file_path": resolved_path,
            "mood": mood
        })
        return True
    
    async def queue_full_update(
        self,
        file_path: str,
        rating: float = None,
        mood: str = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Queue a full metadata update.
        """
        if not self.enabled:
            return False
        
        resolved_path = self._resolve_path(file_path)
        if not resolved_path:
            return False
        
        self.queue.put({
            "operation": "full",
            "file_path": resolved_path,
            "rating": rating,
            "mood": mood,
            "metadata": metadata or {}
        })
        return True
    
    def get_queue_size(self) -> int:
        """Get number of pending tag operations"""
        return self.queue.qsize()
    
    # ========================================
    # TAG WRITING (Synchronous, runs in worker)
    # ========================================
    
    def _write_rating(self, file_path: str, rating: float, play_count: int = 0):
        """
        Write rating to POPM frame.
        
        POPM rating scale (0-255):
        - 1 star: 1
        - 2 stars: 64
        - 3 stars: 128
        - 4 stars: 196
        - 5 stars: 255
        """
        try:
            # Convert 0-5 scale to 0-255
            popm_rating = int(min(max(rating, 0), 5) * 51)
            
            audio = MP3(file_path)
            
            # Ensure ID3 tags exist
            if audio.tags is None:
                audio.add_tags()
            
            # Add/update POPM frame
            audio.tags.add(POPM(
                email=POPM_EMAIL,
                rating=popm_rating,
                count=play_count
            ))
            
            audio.save()
            logger.debug(f"Wrote rating {rating} (POPM {popm_rating}) to {Path(file_path).name}")
            
        except Exception as e:
            logger.error(f"Failed to write rating to {file_path}: {e}")
    
    def _write_mood(self, file_path: str, mood: str):
        """
        Write mood to TXXX and COMM frames.
        """
        try:
            audio = MP3(file_path)
            
            if audio.tags is None:
                audio.add_tags()
            
            # TXXX frame for DJ software
            audio.tags.add(TXXX(
                encoding=3,  # UTF-8
                desc="YOURPARTY_MOOD",
                text=[mood]
            ))
            
            # COMM frame for human readability
            description = MOOD_DESCRIPTIONS.get(mood, mood)
            audio.tags.add(COMM(
                encoding=3,
                lang="eng",
                desc="Mood",
                text=[description]
            ))
            
            audio.save()
            logger.debug(f"Wrote mood '{mood}' to {Path(file_path).name}")
            
        except Exception as e:
            logger.error(f"Failed to write mood to {file_path}: {e}")
    
    def _write_full_metadata(
        self,
        file_path: str,
        rating: float = None,
        mood: str = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Write all metadata in a single operation.
        """
        try:
            audio = MP3(file_path)
            
            if audio.tags is None:
                audio.add_tags()
            
            # Rating
            if rating is not None:
                popm_rating = int(min(max(rating, 0), 5) * 51)
                audio.tags.add(POPM(
                    email=POPM_EMAIL,
                    rating=popm_rating,
                    count=0
                ))
            
            # Mood
            if mood:
                audio.tags.add(TXXX(
                    encoding=3,
                    desc="YOURPARTY_MOOD",
                    text=[mood]
                ))
                audio.tags.add(COMM(
                    encoding=3,
                    lang="eng",
                    desc="Mood",
                    text=[MOOD_DESCRIPTIONS.get(mood, mood)]
                ))
            
            # Optional metadata
            if metadata:
                if metadata.get("title"):
                    audio.tags.add(TIT2(encoding=3, text=[metadata["title"]]))
                if metadata.get("artist"):
                    audio.tags.add(TPE1(encoding=3, text=[metadata["artist"]]))
                if metadata.get("album"):
                    audio.tags.add(TALB(encoding=3, text=[metadata["album"]]))
                if metadata.get("genre"):
                    audio.tags.add(TXXX(
                        encoding=3,
                        desc="YOURPARTY_GENRE",
                        text=[metadata["genre"]]
                    ))
                if metadata.get("bandcamp_url"):
                    audio.tags.add(TXXX(
                        encoding=3,
                        desc="BANDCAMP_URL",
                        text=[metadata["bandcamp_url"]]
                    ))
            
            audio.save()
            logger.info(f"Full metadata update: {Path(file_path).name}")
            
        except Exception as e:
            logger.error(f"Failed to write full metadata to {file_path}: {e}")
    
    # ========================================
    # HELPERS
    # ========================================
    
    def _resolve_path(self, file_path: str) -> Optional[str]:
        """
        Resolve file path, handling different environments.
        """
        if not file_path:
            return None
        
        # Direct check
        if os.path.exists(file_path):
            return file_path
        
        # Try library root mapping
        if self.library_root:
            # Handle Windows paths
            normalized = file_path.replace("\\", "/")
            
            # Extract relative path
            for prefix in [
                "Z:/yourparty_Libary/",
                "Z:/radio_library/",
                "/mnt/music_hdd/",
                "/var/radio/music/",
                "/var/azuracast/stations/yourparty/media/",
                "/var/azuracast/music_storage/",
                "Music/"
            ]:
                if prefix in normalized:
                    relative = normalized.split(prefix)[-1]
                    candidate = os.path.join(self.library_root, relative)
                    if os.path.exists(candidate):
                        return candidate
        
        logger.warning(f"Could not resolve path: {file_path}")
        return None


# Singleton instance
_tagger_service: Optional[AsyncTaggerService] = None


def get_tagger_service() -> AsyncTaggerService:
    """Get or create singleton tagger service"""
    global _tagger_service
    if _tagger_service is None:
        _tagger_service = AsyncTaggerService()
    return _tagger_service


# ========================================
# CONVENIENCE FUNCTIONS
# ========================================

async def tag_rating(file_path: str, rating: float) -> bool:
    """Write rating to file (async, non-blocking)"""
    return await get_tagger_service().queue_rating(file_path, rating)


async def tag_mood(file_path: str, mood: str) -> bool:
    """Write mood to file (async, non-blocking)"""
    return await get_tagger_service().queue_mood(file_path, mood)
