import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
from mutagen.oggvorbis import OggVorbis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {'.mp3', '.flac', '.m4a', '.ogg', '.wav'}

class MusicScanner:
    def __init__(self):
        pass

    def scan_directory(self, path: str) -> List[Dict[str, Any]]:
        """
        Recursively scans a directory for music files and extracts metadata.
        """
        music_files = []
        path = Path(path)

        if not path.exists():
            logger.error(f"Directory not found: {path}")
            return []

        for root, dirs, files in os.walk(path):
            # Modify dirs in-place to skip system/hidden folders
            dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('$') and d != 'System Volume Information']
            
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                    metadata = self._extract_metadata(file_path)
                    music_files.append({
                        "path": str(file_path),
                        "filename": file,
                        "metadata": metadata
                    })
        
        logger.info(f"Found {len(music_files)} music files in {path}")
        return music_files

    def _extract_metadata(self, file_path: Path) -> Dict[str, str]:
        """
        Extracts metadata from a music file using Mutagen.
        """
        metadata = {
            "title": "",
            "artist": "",
            "album": "",
            "genre": "",
            "year": "",
            "duration": 0
        }

        try:
            audio = mutagen.File(file_path)
            if not audio:
                return metadata

            # Duration
            if hasattr(audio, 'info') and hasattr(audio.info, 'length'):
                metadata['duration'] = audio.info.length

            # Tag extraction based on file type
            if file_path.suffix.lower() == '.mp3':
                self._extract_mp3_tags(audio, metadata)
            elif file_path.suffix.lower() == '.flac':
                self._extract_flac_tags(audio, metadata)
            elif file_path.suffix.lower() == '.m4a':
                self._extract_m4a_tags(audio, metadata)
            
            # Fallback for generic Mutagen handling if specific extraction missed something
            # or for other formats
            if not metadata['title']:
                 tags = audio.tags
                 if tags:
                    metadata['title'] = str(tags.get('title', [''])[0])
                    metadata['artist'] = str(tags.get('artist', [''])[0])
                    metadata['album'] = str(tags.get('album', [''])[0])
                    metadata['genre'] = str(tags.get('genre', [''])[0])
                    metadata['year'] = str(tags.get('date', [''])[0])

        except Exception as e:
            logger.warning(f"Error reading metadata from {file_path}: {e}")

        return metadata

    def _extract_mp3_tags(self, audio, metadata):
        # EasyID3 is easier for standard tags
        try:
            tags = EasyID3(audio.filename)
            metadata['title'] = tags.get('title', [''])[0]
            metadata['artist'] = tags.get('artist', [''])[0]
            metadata['album'] = tags.get('album', [''])[0]
            metadata['genre'] = tags.get('genre', [''])[0]
            metadata['year'] = tags.get('date', [''])[0]
        except Exception:
            pass # Fallback to standard mutagen

    def _extract_flac_tags(self, audio, metadata):
        if hasattr(audio, 'tags'):
            metadata['title'] = audio.tags.get('title', [''])[0]
            metadata['artist'] = audio.tags.get('artist', [''])[0]
            metadata['album'] = audio.tags.get('album', [''])[0]
            metadata['genre'] = audio.tags.get('genre', [''])[0]
            metadata['year'] = audio.tags.get('date', [''])[0]

    def _extract_m4a_tags(self, audio, metadata):
        if hasattr(audio, 'tags'):
            # M4A tags often use different keys
            metadata['title'] = audio.tags.get('\xa9nam', [''])[0]
            metadata['artist'] = audio.tags.get('\xa9ART', [''])[0]
            metadata['album'] = audio.tags.get('\xa9alb', [''])[0]
            metadata['genre'] = audio.tags.get('\xa9gen', [''])[0]
            metadata['year'] = audio.tags.get('\xa9day', [''])[0]

if __name__ == "__main__":
    # Test run
    scanner = MusicScanner()
    # Create a dummy file to test if not exists? No, just run.
    print("Scanner initialized.")
