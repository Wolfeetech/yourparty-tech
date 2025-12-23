#!/usr/bin/env python3
"""
Auto-Sort Ratings Script

Moves tracks with average rating < 2.0 and >= 10 votes to /aussortiert/ folder.
Run via cron every 30 minutes: */30 * * * * python3 /app/auto_sort_ratings.py
"""

import os
import shutil
import logging
from datetime import datetime
from pymongo import MongoClient

# Configuration
MONGO_HOST = os.getenv("MONGO_HOST", "192.168.178.222")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_USER = os.getenv("MONGO_USER", "root")
MONGO_PWD = os.getenv("MONGO_PASSWORD", "")

# Paths - AzuraCast media structure
MUSIC_BASE = "/var/azuracast/stations/radio4yourparty/media"
AUSSORTIERT_FOLDER = os.path.join(MUSIC_BASE, "aussortiert")

# Thresholds
MIN_VOTES = 10
MAX_RATING = 2.0

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/auto_sort_ratings.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def get_mongo_client():
    """Connect to MongoDB."""
    if MONGO_USER and MONGO_PWD:
        uri = f"mongodb://{MONGO_USER}:{MONGO_PWD}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"
    else:
        uri = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"
    
    return MongoClient(uri, serverSelectionTimeoutMS=5000)


def get_all_ratings():
    """Fetch all ratings from MongoDB."""
    try:
        client = get_mongo_client()
        db = client.yourparty
        ratings = db.ratings.find()
        return list(ratings)
    except Exception as e:
        logger.error(f"Failed to fetch ratings: {e}")
        return []


def find_file_by_song_id(song_id, base_path):
    """
    Find the actual file path for a song_id.
    Song IDs in AzuraCast are often MD5 hashes or the filename.
    """
    # First check if song_id contains path info
    if song_id and os.path.exists(song_id):
        return song_id
    
    # Search in media folder
    for root, dirs, files in os.walk(base_path):
        # Skip aussortiert folder
        if 'aussortiert' in root:
            continue
        
        for file in files:
            if file.lower().endswith(('.mp3', '.flac', '.m4a', '.ogg')):
                filepath = os.path.join(root, file)
                # Check if song_id matches filename (without extension)
                basename = os.path.splitext(file)[0]
                if song_id == basename or song_id in filepath:
                    return filepath
    
    return None


def move_to_aussortiert(filepath):
    """Move a file to the aussortiert folder."""
    if not os.path.exists(filepath):
        logger.warning(f"File not found: {filepath}")
        return False
    
    # Create aussortiert folder if not exists
    os.makedirs(AUSSORTIERT_FOLDER, exist_ok=True)
    
    filename = os.path.basename(filepath)
    dest_path = os.path.join(AUSSORTIERT_FOLDER, filename)
    
    # Handle duplicates
    if os.path.exists(dest_path):
        base, ext = os.path.splitext(filename)
        dest_path = os.path.join(AUSSORTIERT_FOLDER, f"{base}_{datetime.now().strftime('%Y%m%d')}{ext}")
    
    try:
        shutil.move(filepath, dest_path)
        logger.info(f"Moved to aussortiert: {filename}")
        return True
    except Exception as e:
        logger.error(f"Failed to move {filename}: {e}")
        return False


def auto_sort():
    """Main sorting function."""
    logger.info("=" * 50)
    logger.info("Starting auto-sort check...")
    
    ratings = get_all_ratings()
    logger.info(f"Found {len(ratings)} rated tracks")
    
    moved_count = 0
    candidates = []
    
    for rating in ratings:
        song_id = rating.get('_id') or rating.get('song_id')
        avg = rating.get('average', 5.0)
        total = rating.get('total', 0)
        title = rating.get('title', 'Unknown')
        path = rating.get('path', '')
        
        # Check if meets criteria
        if avg < MAX_RATING and total >= MIN_VOTES:
            candidates.append({
                'song_id': song_id,
                'title': title,
                'average': avg,
                'total': total,
                'path': path
            })
    
    logger.info(f"Found {len(candidates)} tracks below threshold (< {MAX_RATING} stars, >= {MIN_VOTES} votes)")
    
    for track in candidates:
        logger.info(f"  → {track['title']}: {track['average']:.1f} ★ ({track['total']} votes)")
        
        # Try to find and move the file
        filepath = track.get('path')
        if not filepath or not os.path.exists(filepath):
            filepath = find_file_by_song_id(track['song_id'], MUSIC_BASE)
        
        if filepath and os.path.exists(filepath):
            if move_to_aussortiert(filepath):
                moved_count += 1
        else:
            logger.warning(f"  Could not find file for: {track['title']}")
    
    logger.info(f"Auto-sort complete. Moved {moved_count} tracks.")
    logger.info("=" * 50)
    
    return moved_count


if __name__ == "__main__":
    auto_sort()
