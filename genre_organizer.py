import os
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GenreOrganizer:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)

    def organize_file(self, file_path: str, metadata: Dict[str, Any], dry_run: bool = False, output_path: str = None) -> Dict[str, Any]:
        """
        Moves or copies a file to a genre-based directory structure.
        Structure: Base / Genre / Artist - Title.ext
        If output_path is provided, it is used as the base destination.
        """
        source_path = Path(file_path)
        if not source_path.exists():
            return {"success": False, "error": "File not found"}

        # Professional Structure: Genre / Artist / Album / Track - Title.ext
        genre = metadata.get('genre', 'Unknown Genre')
        artist = metadata.get('artist', 'Unknown Artist')
        title = metadata.get('title', 'Unknown Title')

        # If Genre has multiple values (comma separated), take the first one for the folder
        primary_genre = genre.split(',')[0].strip()
        
        # Sanitize components
        def sanitize(s):
            return "".join([c for c in s if c.isalnum() or c in (' ', '-', '_', '.', '(', ')', ',')]).strip()

        safe_genre = sanitize(primary_genre)
        safe_artist = sanitize(artist)
        safe_album = sanitize(metadata.get('album', 'Unknown Album'))
        safe_title = sanitize(title)
        
        # Build filename
        # If we have track number, include it? (Not in current metadata, maybe add later)
        # For now: Artist - Title.ext
        safe_filename = f"{safe_artist} - {safe_title}"
        
        # Determine target base
        target_base = Path(output_path) if output_path else self.base_path
        
        # Structure: Genre/Artist/Album/
        target_dir = target_base / safe_genre / safe_artist / safe_album
        target_path = target_dir / f"{safe_filename}{source_path.suffix}"

        # Handle duplicates
        counter = 1
        while target_path.exists() and target_path != source_path:
            target_path = target_dir / f"{safe_filename} ({counter}){source_path.suffix}"
            counter += 1

        result = {
            "source": str(source_path),
            "destination": str(target_path),
            "genre": genre,
            "success": False,
            "dry_run": dry_run
        }

        if source_path == target_path:
            result["success"] = True
            result["message"] = "File already in correct location"
            return result

        try:
            if not dry_run:
                target_dir.mkdir(parents=True, exist_ok=True)
                # Use shutil.copy2 then unlink for cross-device moves (safer than move)
                # Or just copy if user wants to keep originals? 
                # Request said "sortieren", usually implies moving.
                # But for SMB, copy is safer. Let's do copy + delete (move behavior)
                
                shutil.copy2(str(source_path), str(target_path))
                
                # Only delete source if we are NOT just copying to a new export location
                # If output_path is different from base_path (source root), maybe we should keep source?
                # The user asked for "sorting", so let's assume move.
                # But if it's a network share, maybe they want to keep local backup?
                # Let's default to MOVE for now as per "sorting".
                
                try:
                    os.unlink(str(source_path))
                except Exception as e:
                    logger.warning(f"Could not delete source file {source_path}: {e}")
                    
                logger.info(f"Moved {source_path} to {target_path}")
            
            result["success"] = True
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error moving file: {e}")

        return result

if __name__ == "__main__":
    pass
