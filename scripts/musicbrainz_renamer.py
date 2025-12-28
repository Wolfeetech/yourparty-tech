#!/usr/bin/env python3
"""
MusicBrainz Renamer Script
==========================
Scans Z:\yourparty_Libary\Inbox, identifies tracks via MusicBrainz,
and renames/moves them to a clean folder structure.

Structure: Z:\yourparty_Libary\Genre\Artist\Album\Track - Title.ext
"""
import os
import sys
import shutil
import logging
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(PROJECT_ROOT, "apps", "api"))

from tag_improver import TagImprover
from music_scanner import MusicScanner
from genre_organizer import GenreOrganizer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MusicBrainzRenamer")

# Configuration
LIBRARY_DIR = os.getenv("LIBRARY_ROOT_WIN", r"Z:\yourparty_Libary")
INBOX_DIR = os.path.join(LIBRARY_DIR, "Inbox")
ARCHIVE_DIR = os.path.join(LIBRARY_DIR, "Archive")  # Failed/unknown files

def ensure_dirs():
    """Create required directories if missing."""
    for d in [INBOX_DIR, ARCHIVE_DIR]:
        if not os.path.exists(d):
            os.makedirs(d)
            logger.info(f"Created directory: {d}")

def rename_and_sort():
    """Main renaming and sorting logic."""
    ensure_dirs()
    
    if not os.path.exists(LIBRARY_DIR):
        logger.error(f"Library root not found: {LIBRARY_DIR}")
        return
    
    improver = TagImprover()
    scanner = MusicScanner()
    organizer = GenreOrganizer(LIBRARY_DIR)
    
    logger.info(f"🎵 Scanning Inbox: {INBOX_DIR}")
    
    count_success = 0
    count_failed = 0
    count_archived = 0
    
    for file_entry in scanner.scan_directory(INBOX_DIR):
        file_path = file_entry['path']
        original_metadata = file_entry['metadata']
        basename = os.path.basename(file_path)
        
        logger.info(f"--- Processing: {basename} ---")
        
        # 1. Try to identify via MusicBrainz
        mb_result = improver.improve_tags(file_path)
        
        if mb_result['success'] and mb_result['confidence'] >= 0.8:
            metadata = mb_result['metadata']
            logger.info(f"✅ Identified: {metadata.get('artist')} - {metadata.get('title')}")
        else:
            # Fallback to existing/parsed metadata
            metadata = original_metadata
            logger.warning(f"⚠️ MusicBrainz match failed, using existing tags")
        
        # 2. Validate minimum metadata
        if not metadata.get('title') or metadata.get('title') == 'Unknown Title':
            # Move to Archive for manual review
            archive_path = os.path.join(ARCHIVE_DIR, basename)
            try:
                shutil.move(file_path, archive_path)
                logger.info(f"📦 Archived (insufficient metadata): {basename}")
                count_archived += 1
            except Exception as e:
                logger.error(f"Failed to archive {basename}: {e}")
            continue
        
        # 3. Organize into Library
        result = organizer.organize_file(file_path, metadata, dry_run=False)
        
        if result['success']:
            count_success += 1
            logger.info(f"✅ Moved to: {result['destination']}")
        else:
            count_failed += 1
            logger.error(f"❌ Failed to organize: {result.get('error')}")
    
    logger.info(f"\n🏁 Complete! Success: {count_success}, Failed: {count_failed}, Archived: {count_archived}")

if __name__ == "__main__":
    rename_and_sort()
