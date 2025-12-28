
import os
import shutil
import logging
import sys
from pathlib import Path

# Fix import path (add project root to sys.path)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(PROJECT_ROOT, "apps", "api"))

from genre_organizer import GenreOrganizer
from music_scanner import MusicScanner

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("LibraryReorg")

# Configuration
SOURCE_DIR = r"M:\Inbox"  # Unsorted files go here
LIBRARY_DIR = r"M:\Library" # Sorted files go here
ARCHIVE_DIR = r"M:\Archive" # Corrupt/Unknown files go here

def ensure_dirs():
    """Create the base directory structure if missing."""
    for d in [SOURCE_DIR, LIBRARY_DIR, ARCHIVE_DIR]:
        if not os.path.exists(d):
            os.makedirs(d)
            logger.info(f"Created directory: {d}")

def reorganize_inbox():
    """
    Scans the Inbox and organizes files into the Library.
    Structure: Library/Genre/Artist/Album/Track.ext
    """
    ensure_dirs()
    
    organizer = GenreOrganizer(LIBRARY_DIR)
    scanner = MusicScanner()
    
    logger.info(f"Scanning Inbox: {SOURCE_DIR}...")
    
    count_success = 0
    count_fail = 0
    
    # Use scanner to get metadata
    # scan_directory yields dicts with 'path', 'metadata'
    for file_entry in scanner.scan_directory(SOURCE_DIR):
        file_path = file_entry['path']
        metadata = file_entry['metadata']
        
        logger.info(f"Processing: {os.path.basename(file_path)}")
        
        # Determine if we have enough metadata to file it
        if not metadata.get('genre') or metadata.get('genre') == 'Unknown Genre':
             # Try to infer or move to Review folder?
             # For now, let organizer handle it (it uses "Unknown Genre" folder)
             pass
             
        result = organizer.organize_file(
            file_path, 
            metadata, 
            dry_run=False, 
            output_path=LIBRARY_DIR
        )
        
        if result['success']:
            count_success += 1
            # If organizer moved it, we are good.
        else:
            count_fail += 1
            logger.error(f"Failed to organize {file_path}: {result.get('error')}")

    logger.info(f"Reorganization Complete. Sorted: {count_success}, Failed: {count_fail}")

if __name__ == "__main__":
    # Safety Check
    if not os.path.exists("M:\\"):
        logger.error("Drive M: is not mounted! Cannot run reorganization.")
    else:
        ensure_dirs()
        print("Folder structure verified: Inbox, Library, Archive.")
        print("Starting reorganization...")
        reorganize_inbox()
