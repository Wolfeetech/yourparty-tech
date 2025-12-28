
import os
import sys
import logging

# Setup logging to stdout
logging.basicConfig(level=logging.INFO)

# Adjust path to find modules
sys.path.insert(0, os.path.dirname(__file__))

from library_service import LibraryService

# Define path (prefer library root, fallback to legacy env)
MUSIC_DIR = os.getenv(
    "LIBRARY_ROOT_LINUX",
    os.getenv("MUSIC_DIR", "/var/radio/music/yourparty_Libary")
)

print(f"Starting force scan on {MUSIC_DIR}...")
try:
    service = LibraryService(MUSIC_DIR)
    service.run_ingestion()
    print("Scan complete.")
except Exception as e:
    print(f"Scan failed: {e}")
