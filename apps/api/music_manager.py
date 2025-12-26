import os
import logging
from pathlib import Path
from typing import Optional, Dict
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TXXX, COMM, TIT2, TPE1, TALB
from pymongo import MongoClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
MONGO_URI = "mongodb://root:4f5cd00532af49b5941d6f6385b2e0bf@192.168.178.222:27017/?authSource=admin"
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
            
            # TODO: Improve matching logic
            # Try exact match on 'filename' field in tracks
            track_doc = self.tracks_col.find_one({"filename": filename})
            
            if not track_doc:
                return # No data for this track

            # 2. Aggregating Moods/Votes
            song_id = track_doc.get('song_id') or str(track_doc.get('_id'))
            
            # Fetch derived moods (if we have a summary collection, use that, else aggregate)
            # For this MVP, let's look for 'song_metadata' entries
            metadata_doc = self.meta_col.find_one({"song_id": song_id})
            
            start_rating = 0
            mood_tags = []
            
            if metadata_doc:
               # Example structure needed
               pass

            # If no metadata doc, check raw polls? 
            # User said "votes aus dem online stream". This is likely in 'moods' collection.
            # We need to aggregate.
            
            # Simple Aggregation
            mood_votes = self.moods_col.aggregate([
                {"$match": {"song_id": song_id}},
                {"$group": {"_id": "$mood", "count": {"$sum": 1}}}
            ])
            
            top_moods = []
            for m in mood_votes:
                if m['count'] > 0: # Threshold?
                    top_moods.append(f"{m['_id']}:{m['count']}")
            
            if not top_moods:
                return # Nothing to write

            mood_str = ", ".join(top_moods)
            
            # 3. Write to Tags
            audio = mutagen.File(file_path)
            
            if file_path.suffix.lower() == '.mp3':
                # Write to TXXX frame for custom data, or COMMENT
                if audio.tags is None:
                    audio.add_tags()
                
                # Using TXXX:MOOD
                audio.tags.add(TXXX(encoding=3, desc='MOOD', text=[mood_str]))
                # Also write to Comment for visibility in basic players
                audio.tags.add(COMM(encoding=3, lang='eng', desc='YourPartyMoods', text=[mood_str]))
                
                if not dry_run:
                    audio.save()
                    logger.info(f"Updated {filename} -> Moods: {mood_str}")
                else:
                    logger.info(f"[DRY] Would update {filename} -> Moods: {mood_str}")

        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}")

if __name__ == "__main__":
    # Default to a test path or mapped drive
    # We need the user to tell us the path, or we guess 'Z:'
    path = "Z:\\" 
    manager = MusicManager(path)
    manager.sync_metadata(dry_run=True)
