
import os
import shutil
import logging
import hashlib
from pathlib import Path
import mutagen
from mutagen.easyid3 import EasyID3

# Config
DESTINATION_ROOT = Path("Z:/radio_library")
LOG_FILE = "migration.log"

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MusicOrganizer")

def get_file_hash(file_path):
    """Calculates SHA256 hash to detect duplicates."""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        # Read in blocks
        for block in iter(lambda: f.read(4096), b""):
            hasher.update(block)
    return hasher.hexdigest()

def clean_name(name):
    """Sanitizes strings for folder names."""
    if not name:
        return "Unknown"
    # Replace bad chars
    keepcharacters = (' ','.','_','-')
    return "".join(c for c in name if c.isalnum() or c in keepcharacters).strip()

def get_metadata(file_path):
    """Extracts basic metadata (Artist, Album, Genre)."""
    meta = {
        "artist": "Unknown Artist",
        "album": "Unknown Album",
        "genre": "Unsorted",
        "title": file_path.stem
    }
    
    try:
        audio = mutagen.File(file_path, easy=True)
        if audio:
            # Handle list vs string
            def get_first(key):
                val = audio.get(key)
                if val:
                    return val[0] if isinstance(val, list) else val
                return None

            artist = get_first('artist')
            album = get_first('album')
            genre = get_first('genre')
            title = get_first('title')

            if artist: meta['artist'] = clean_name(artist)
            if album: meta['album'] = clean_name(album)
            if genre: meta['genre'] = clean_name(genre)
            if title: meta['title'] = clean_name(title)
            
    except Exception as e:
        logger.warning(f"Metadata read error on {file_path}: {e}")
        
    return meta

def process_file(file_path):
    """Moves a single file to the structured destination."""
    file_path = Path(file_path)
    
    # 1. Get Metadata
    meta = get_metadata(file_path)
    
    # 2. Build Destination Path
    # Structure: Z:\radio_library\Genre\Artist\Album\Filename.ext
    target_dir = DESTINATION_ROOT / meta['genre'] / meta['artist'] / meta['album']
    target_file = target_dir / file_path.name
    
    # 3. Check Duplicate
    if target_file.exists():
        logger.info(f"Duplicate found: {target_file.name} (Checking Hash...)")
        if get_file_hash(file_path) == get_file_hash(target_file):
            logger.info("❌ Exact duplicate. Skipping.")
            return
        else:
            # Name collision but different file - rename
            target_file = target_dir / f"{file_path.stem}_{get_file_hash(file_path)[:6]}{file_path.suffix}"

    # 4. Move File
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, target_file) # Copy first to be safe
        # shutil.move(file_path, target_file) # Uncomment to actually Move
        logger.info(f"✅ Migrated: {file_path.name} -> {meta['genre']}/{meta['artist']}")
    except Exception as e:
        logger.error(f"Failed to copy {file_path}: {e}")

def run_organizer(source_dir):
    source_path = Path(source_dir)
    if not source_path.exists():
        logger.error(f"Source not found: {source_dir}")
        return

    logger.info(f"🚀 Starting Migration from {source_dir} -> {DESTINATION_ROOT}")
    
    extensions = {'.mp3', '.flac', '.m4a', '.aiff', '.wav', '.ogg'}
    
    count = 0
    for root, _, files in os.walk(source_path):
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix.lower() in extensions:
                process_file(file_path)
                count += 1
                if count % 50 == 0:
                    print(f"Processed {count} files...")

    logger.info(f"🏁 Complete. Processed {count} files.")

if __name__ == "__main__":
    import sys
    # Default to user music or arg
    default_src = Path.home() / "Music"
    
    if len(sys.argv) > 1:
        src = sys.argv[1]
    else:
        src = input(f"Enter source directory [Default: {default_src}]: ") or default_src
        
    run_organizer(src)
