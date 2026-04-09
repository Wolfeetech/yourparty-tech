import os
import logging
from music_scanner import MusicScanner

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_scan():
    print("--- DEBUG SCAN STARTED ---")
    scanner = MusicScanner()
    path = os.getenv("LIBRARY_ROOT_LINUX", "/var/radio/music/yourparty_Libary")
    
    print(f"Scanning: {path}")
    if not os.path.exists(path):
        print(f"❌ Path does not exist: {path}")
        return

    try:
        files = scanner.scan_directory(path)
        print(f"✅ Scan Complete. Found {len(files)} files.")
        if len(files) > 0:
            print(f"Sample: {files[0]}")
    except Exception as e:
        print(f"❌ CRASH: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_scan()
