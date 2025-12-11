import os
import logging
from mutagen.id3 import ID3, POPM, TXXX, COMM
from mutagen.mp3 import MP3

logger = logging.getLogger(__name__)

def write_metadata_to_file(file_path: str, rating: float = None, mood: str = None):
    """
    Writes rating and mood directly to the MP3 file ID3 tags.
    This ensures data persistence even if the database is lost.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found for tagging: {file_path}")
        return False
        
    try:
        from mutagen import File
        from mutagen.id3 import ID3, POPM, TXXX
        from mutagen.flac import FLAC
        
        audio = File(file_path)
        
        if audio is None:
            logger.error(f"Could not open file (unknown format): {file_path}")
            return False

        # Handle ID3 (MP3, AIFF, etc.)
        if hasattr(audio, 'tags') and isinstance(audio.tags, ID3):
             # 1. Write Rating
            if rating is not None:
                val = int((rating / 5.0) * 255)
                audio.tags.add(POPM(email='yourparty', rating=val))
                audio.tags.add(TXXX(encoding=3, desc='RATING', text=str(rating)))
            
            # 2. Write Mood
            if mood:
                audio.tags.add(TXXX(encoding=3, desc='MOOD', text=mood))
            
            audio.save()
            
        # Handle FLAC / Vorbis Comments
        elif isinstance(audio, FLAC) or (hasattr(audio, 'tags') and hasattr(audio.tags, 'get')):
            # FLAC uses Vorbis comments. No POPM.
            # Standard for Rating in Vorbis is usually RATING (0-5 or 0-100) or FMPS_RATING
            if rating is not None:
                audio['RATING'] = str(rating) # simple string matches TXXX
                # Maybe scale? But let's keep 1-5 for now or check spec.
                # WMP uses 'RATING' 0-100? None standard. 
                # Let's save as RATING=5
            
            if mood:
                audio['MOOD'] = mood
            
            audio.save()
            
        else:
             logger.warning(f"Unsupported tag format for {file_path}")
             return False

        logger.info(f"Updated tags for {os.path.basename(file_path)}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to write tags: {e}")
        return False
