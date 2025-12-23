import os
import logging
import acoustid
import musicbrainzngs
from typing import Dict, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Keys (Ideally these should be in env vars, but for this local tool we might need to ask user or use a default if allowed)
# For now, I will use placeholders or expect them to be passed/configured.
# AcoustID requires an API key. 
# MusicBrainz requires a user agent.

class TagImprover:
    def __init__(self, acoustid_api_key: str = "cSpUJKpD"): # Using a public demo key or user provided
        self.acoustid_api_key = acoustid_api_key
        musicbrainzngs.set_useragent("MusicLibraryHelper", "0.1", "http://localhost:8000")

    def improve_tags(self, file_path: str) -> Dict[str, Any]:
        """
        Identifies a track using AcoustID and fetches metadata from MusicBrainz.
        """
        # Ensure fpcalc is found
        if os.getcwd() not in os.environ["PATH"]:
            os.environ["PATH"] += os.pathsep + os.getcwd()

        result = {
            "success": False,
            "confidence": 0.0,
            "metadata": {},
            "error": None
        }

        try:
            logger.info(f"Fingerprinting {file_path}...")
            # 1. Fingerprint and Lookup via AcoustID
            # We use match() which does fingerprinting + lookup
            matches = acoustid.match(self.acoustid_api_key, file_path, meta='recordings releases')
            
            best_match = None
            highest_score = 0.0

            for score, recording_id, title, artist in matches:
                logger.info(f"Found match: {title} by {artist} (Score: {score})")
                if score > highest_score:
                    highest_score = score
                    best_match = {
                        "recording_id": recording_id,
                        "title": title,
                        "artist": artist
                    }

            if not best_match:
                logger.warning(f"No matches found for {file_path}")
                result["error"] = "No matches found via AcoustID"
                return result
            
            if highest_score < 0.8: # Threshold
                logger.warning(f"Low confidence match: {highest_score}")
                result["error"] = f"Low confidence match ({highest_score:.2f})"
                return result

            result["confidence"] = highest_score
            logger.info(f"Best match: {best_match['title']} (ID: {best_match['recording_id']})")
            
            # 2. Fetch detailed info from MusicBrainz using the recording_id
            try:
                mb_data = musicbrainzngs.get_recording_by_id(best_match['recording_id'], includes=['artists', 'releases', 'tags', 'genres'])
            except Exception as e:
                logger.error(f"MusicBrainz API error: {e}")
                # Fallback to AcoustID data if MB fails
                result["metadata"] = {
                    "title": best_match['title'],
                    "artist": best_match['artist'],
                    "album": "",
                    "year": "",
                    "genre": ""
                }
                result["success"] = True
                result["warning"] = "MusicBrainz detail fetch failed, used basic data"
                return result
            
            recording = mb_data['recording']
            
            new_metadata = {
                "title": recording.get('title', best_match['title']),
                "artist": best_match['artist'], # Default
                "album": "",
                "year": "",
                "genre": ""
            }

            # Artist
            if 'artist-credit' in recording:
                new_metadata['artist'] = recording['artist-credit'][0]['artist']['name']

            # Album & Year (Take the first release)
            if 'release-list' in recording and len(recording['release-list']) > 0:
                release = recording['release-list'][0]
                new_metadata['album'] = release.get('title', '')
                new_metadata['year'] = release.get('date', '')[:4] if release.get('date') else ""

            # Genre (from tags) - Professional: Get top 3 tags
            if 'tag-list' in recording:
                # Sort by count if available
                tags = sorted(recording['tag-list'], key=lambda x: int(x.get('count', 0)), reverse=True)
                if tags:
                    # Filter out very generic tags if needed, or just take top 3
                    top_tags = [t['name'].title() for t in tags[:3]]
                    new_metadata['genre'] = ", ".join(top_tags)
            
            # Year - Professional: Try to find the earliest release date (Original Release)
            if 'release-list' in recording:
                dates = [r.get('date') for r in recording['release-list'] if r.get('date')]
                if dates:
                    dates.sort() # ISO dates sort correctly as strings
                    new_metadata['year'] = dates[0][:4]
            
            result["metadata"] = new_metadata
            result["success"] = True

        except acoustid.FingerprintGenerationError as e:
             logger.error(f"Fingerprint error: {e}")
             result["error"] = f"Could not generate fingerprint: {e}"
        except acoustid.WebServiceError as e:
            logger.error(f"AcoustID API error: {e}")
            result["error"] = f"AcoustID API error: {e}"
        except Exception as e:
            logger.error(f"Unexpected error improving tags for {file_path}: {e}", exc_info=True)
            result["error"] = f"Unexpected error: {e}"

        return result

if __name__ == "__main__":
    # Test
    improver = TagImprover()
    print("TagImprover initialized")
