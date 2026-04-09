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

SUPPORTED_EXTENSIONS = {'.mp3', '.flac', '.m4a', '.ogg', '.wav', '.aac', '.wma', '.aiff'}

class MusicScanner:
    def __init__(self):
        pass

    def scan_directory(self, path: str):
        """
        Recursively scans a directory for music files and yields metadata.
        NOW A GENERATOR to prevent OOM on large libraries.
        """
        path = Path(path)

        if not path.exists():
            logger.error(f"Directory not found: {path}")
            return

        count = 0
        for root, dirs, files in os.walk(path):
            # Modify dirs in-place to skip system/hidden folders
            dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('$') and d != 'System Volume Information']
            
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                    try:
                        metadata = self._extract_metadata(file_path)
                        yield {
                            "path": str(file_path),
                            "filename": file,
                            "metadata": metadata
                        }
                        count += 1
                        if count % 100 == 0:
                            logger.info(f"Scanned {count} files so far...")
                    except Exception as e:
                        logger.error(f"Error yielding file {file}: {e}")
        
        logger.info(f"Scan complete. Processed {count} files.")

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
            "duration": 0,
            "initial_key": "",
            "bpm": 0
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

            # Final Fallback: Filename Parsing
            if not metadata['title'] or not metadata['artist']:
                filename_meta = self._parse_filename(file_path)
                if not metadata['title']:
                    metadata['title'] = filename_meta.get('title', file_path.stem)
                if not metadata['artist']:
                    metadata['artist'] = filename_meta.get('artist', 'Unknown Artist')

        except Exception as e:
            logger.warning(f"Error reading metadata from {file_path}: {e}")
            # Ensure minimal metadata from filename even on error
            filename_meta = self._parse_filename(file_path)
            metadata['title'] = filename_meta.get('title', file_path.stem)
            metadata['artist'] = filename_meta.get('artist', 'Unknown Artist')

        return metadata

    def _parse_filename(self, file_path: Path) -> Dict[str, str]:
        """Fallback: Try to parse Artist - Title from filename."""
        filename = file_path.stem # No extension
        # Common patterns: "Artist - Title", "01 Artist - Title"
        
        # Remove leading numbers/track numbers if present (simple heuristic)
        # e.g. "01. " or "01 "
        clean_name = filename
        import re
        clean_name = re.sub(r'^\d+[\s.-]+', '', clean_name)
        
        parts = clean_name.split(' - ', 1)
        if len(parts) == 2:
            return {"artist": parts[0].strip(), "title": parts[1].strip()}
        
        return {"title": clean_name}

    def _extract_mp3_tags(self, audio, metadata):
        # EasyID3 is easier for standard tags
        try:
            from mutagen.easyid3 import EasyID3
            try:
                tags = EasyID3(audio.filename)
                metadata['title'] = tags.get('title', [''])[0]
                metadata['artist'] = tags.get('artist', [''])[0]
                metadata['album'] = tags.get('album', [''])[0]
                metadata['genre'] = tags.get('genre', [''])[0]
                metadata['year'] = tags.get('date', [''])[0]
                metadata['bpm'] = tags.get('bpm', [0])[0]
                metadata['initial_key'] = tags.get('initialkey', [''])[0]
            except Exception:
                pass
            
            # 2. Raw ID3 fallback for Key/BPM if missing
            if not metadata['initial_key'] or not metadata['bpm']:
                 if hasattr(audio, 'tags'):
                    # TKEY = Initial Key, TBPM = BPM
                    if 'TKEY' in audio.tags:
                        metadata['initial_key'] = str(audio.tags['TKEY'].text[0])
                    if 'TBPM' in audio.tags:
                        try:
                            metadata['bpm'] = int(str(audio.tags['TBPM'].text[0]))
                        except: pass
        except Exception:
            pass # Fallback to standard mutagen

    def _extract_flac_tags(self, audio, metadata):
        if hasattr(audio, 'tags'):
            metadata['title'] = audio.tags.get('title', [''])[0]
            metadata['artist'] = audio.tags.get('artist', [''])[0]
            metadata['album'] = audio.tags.get('album', [''])[0]
            metadata['genre'] = audio.tags.get('genre', [''])[0]
            metadata['year'] = audio.tags.get('date', [''])[0]
            
            # FLAC usually uses 'INITIAL_KEY' or 'KEY', and 'BPM'
            metadata['bpm'] = audio.tags.get('bpm', [0])[0]
            metadata['initial_key'] = audio.tags.get('initial_key', [''])[0]
            if not metadata['initial_key']:
                 metadata['initial_key'] = audio.tags.get('key', [''])[0]

    def _extract_m4a_tags(self, audio, metadata):
        if hasattr(audio, 'tags'):
            # M4A tags often use different keys
            metadata['title'] = audio.tags.get('\xa9nam', [''])[0]
            metadata['artist'] = audio.tags.get('\xa9ART', [''])[0]
            metadata['album'] = audio.tags.get('\xa9alb', [''])[0]
            metadata['genre'] = audio.tags.get('\xa9gen', [''])[0]
            metadata['year'] = audio.tags.get('\xa9day', [''])[0]
            if 'tmpo' in audio.tags:
                 try:
                     metadata['bpm'] = int(audio.tags['tmpo'][0])
                 except: pass

if __name__ == "__main__":
    # Test run
    scanner = MusicScanner()
    # Create a dummy file to test if not exists? No, just run.
    print("Scanner initialized.")
