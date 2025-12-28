import os
import logging
from pathlib import Path
from typing import Optional, Dict
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TXXX, COMM, TIT2, TPE1, TALB
from pymongo import MongoClient
from config_secrets import (
    MONGO_URI, SMB_USERNAME, SMB_PASSWORD, SMB_SERVER, SMB_SHARE,
    LIBRARY_ROOT_WIN
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DB_NAME = "radio_ratings"

class MusicManager:
    def __init__(self, music_dir: str):
        self.music_dir = Path(music_dir)
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.tracks_col = self.db.tracks
        self.moods_col = self.db.moods
        self.meta_col = self.db.song_metadata

    def sync_metadata(self, dry_run=False):
        """
        Walks the music directory, finds matching Mongo entries, 
        and writes Mood/Rating metadata to ID3 tags.
        """
        if not self.music_dir.exists():
            logger.error(f"Music directory not found: {self.music_dir}")
            return

        logger.info(f"Starting Metadata Sync in {self.music_dir} (Dry Run: {dry_run})")
        
        count = 0
        for root, _, files in os.walk(self.music_dir):
            for file in files:
                if file.lower().endswith(('.mp3', '.flac', '.m4a', '.ogg')):
                    file_path = Path(root) / file
                    self.process_file_sync(file_path, dry_run)
                    count += 1
                    if count % 100 == 0:
                        logger.info(f"Processed {count} files...")

    def process_file_sync(self, file_path: Path, dry_run: bool):
        try:
            # 1. Identify Song (Filename match for now, ideally Hash)
            # We look up in Mongo by filename
            filename = file_path.name
            
            # Match strategy: Filename match on 'file_path' end
            # This handles /var/radio/music/song.mp3 vs Z:\song.mp3
            import re
            track_doc = self.tracks_col.find_one({"file_path": {"$regex": re.escape(filename) + "$"}})
            
            if not track_doc:
                # Fallback: Try exact 'filename' field
                track_doc = self.tracks_col.find_one({"filename": filename})
            
            if not track_doc:
                return # No data for this track

            # 2. Aggregating Moods/Votes
            song_id = track_doc.get('song_id') or str(track_doc.get('_id'))
            
            # Simple Aggregation
            mood_votes = self.moods_col.aggregate([
                {"$match": {"song_id": song_id}},
                {"$group": {"_id": "$mood", "count": {"$sum": 1}}}
            ])
            
            top_moods = []
            for m in mood_votes:
                if m['count'] > 0: 
                    top_moods.append(f"{m['_id']}:{m['count']}")
            
            if not top_moods:
                # Check explicit metadata rating/mood if votes are empty?
                 pass

            mood_str = ", ".join(top_moods)
            if not mood_str:
                 return

            # 3. Write to Tags
            try:
                audio = mutagen.File(file_path)
                if not audio.tags:
                    audio.add_tags()

                is_updated = False
                
                # MP3 (ID3)
                if file_path.suffix.lower() == '.mp3':
                    # TXXX:MOOD
                    audio.tags.add(TXXX(encoding=3, desc='MOOD', text=[mood_str]))
                    audio.tags.add(COMM(encoding=3, lang='eng', desc='YourPartyMoods', text=[mood_str]))
                    # Rating? POPM
                    is_updated = True
                    
                # FLAC (Vorbis)
                elif file_path.suffix.lower() == '.flac':
                    audio.tags['MOOD'] = mood_str
                    audio.tags['RATING'] = mood_str # Or calculate integer
                    is_updated = True
                
                # M4A (MP4)
                elif file_path.suffix.lower() == '.m4a':
                    audio.tags['----:com.apple.iTunes:MOOD'] = mood_str.encode('utf-8')
                    is_updated = True

                if is_updated:
                    if not dry_run:
                        audio.save()
                        logger.info(f"Updated {filename} -> Moods: {mood_str}")
                    else:
                        logger.info(f"[DRY] Would update {filename} -> Moods: {mood_str}")
            except Exception as e:
                logger.error(f"Error saving tags for {filename}: {e}")

        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}")

if __name__ == "__main__":
    import subprocess
    import sys
    
    # 1. Mount Drive
    drive_letter = Path(LIBRARY_ROOT_WIN).drive or "Z:"
    unc_path = f"\\\\{SMB_SERVER}\\{SMB_SHARE}"
    
    print(f"🔌 Mounting {unc_path} to {drive_letter}...")
    
    # Clean up first
    subprocess.run(f"net use {drive_letter} /delete /y", shell=True, stderr=subprocess.DEVNULL)
    
    # Mount
    cmd = f'net use {drive_letter} "{unc_path}" /USER:{SMB_USERNAME} "{SMB_PASSWORD}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Failed to mount drive: {result.stderr}")
        print("Please check credentials in apps/api/secrets.py")
        sys.exit(1)
        
    print("✅ Drive mounted successfully.")

    # 2. Run Sync
    try:
        manager = MusicManager(LIBRARY_ROOT_WIN)
        # Default to dry_run=False since we want to fix it now
        manager.sync_metadata(dry_run=False)
    finally:
        # Optional: Unmount? user might want to keep it.
        pass
