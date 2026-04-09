
import os
import logging
import requests
import urllib3
from dotenv import load_dotenv
from apps.api.mongo_client import MongoDatabaseClient

# Load Env
load_dotenv('/opt/radio-api/.env')
load_dotenv()

# Config
MONGO_URI = os.getenv("MONGO_URI")
# Force HTTPS
AZURACAST_API_URL = os.getenv("AZURACAST_URL", "https://radio.yourparty.tech/api").replace('http:', 'https:').rstrip('/')
if not AZURACAST_API_URL.endswith('/api'): AZURACAST_API_URL += '/api'
AZURACAST_API_KEY = os.getenv("AZURACAST_API_KEY")
HEADERS = {"Authorization": f"Bearer {AZURACAST_API_KEY}"}

# Valid Moods Mapping (flexible matching)
MOOD_MAPPING = {
    # ENERGY (High energy, uplifting, main-stage)
    "energy": "ENERGY", "energetic": "ENERGY", "uplifting": "ENERGY",
    "electronic": "ENERGY", "dance": "ENERGY", "edm": "ENERGY",
    "rock": "ENERGY", "pop": "ENERGY", "drum & bass": "ENERGY", "dnb": "ENERGY",
    
    # CHILL (Relaxed, slow, lounge)
    "chill": "CHILL", "chillout": "CHILL", "ambient": "CHILL",
    "downtempo": "CHILL", "lounge": "CHILL", "r&b": "CHILL", "soul": "CHILL",
    "jazz": "CHILL",
    
    # DARK (Techno, bass, heavy)
    "dark": "DARK", "techno": "DARK", "minimal": "DARK",
    "bass": "DARK", "dubstep": "DARK", "industrial": "DARK",
    
    # GROOVE (House, Funk, Disco)
    "groove": "GROOVE", "house": "GROOVE", "disco": "GROOVE",
    "funk": "GROOVE", "hip hop": "GROOVE", "rap": "GROOVE",
    "tech house": "GROOVE", "deep house": "GROOVE",
    
    # EUPHORIC (Trance, emotional)
    "euphoric": "EUPHORIC", "trance": "EUPHORIC", "progressive": "EUPHORIC",
    "emotional": "EUPHORIC"
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GenreImport")
urllib3.disable_warnings()

def main():
    logger.info(f"Connecting to DB: {MONGO_URI}...")
    db_client = MongoDatabaseClient(MONGO_URI, database_name="yourparty")
    db = db_client.db
    
    logger.info(f"Fetching Media from {AZURACAST_API_URL}...")
    try:
        url = f"{AZURACAST_API_URL}/station/1/files"
        resp = requests.get(url, headers=HEADERS, verify=False, timeout=60)
        resp.raise_for_status()
        tracks = resp.json()
    except Exception as e:
        logger.error(f"Failed to fetch AzuraCast media: {e}")
        return

    logger.info(f"Processing {len(tracks)} tracks...")
    imported_count = 0
    
    debug_limit = 20
    for t in tracks:
        ac_id = t.get('id')
        title = t.get('title')
        raw_genre = t.get('genre')
        genre = (raw_genre or '').lower().strip()
        
        if debug_limit > 0:
            print(f"DEBUG: ID={ac_id} | Genre='{raw_genre}' -> '{genre}'")
            debug_limit -= 1
        
        if not genre or not ac_id:
            continue
            
        # Check mapping
        mood = None
        for key, val in MOOD_MAPPING.items():
            if key in genre:
                mood = val
                break
        
        if mood:
            # We need a song_id. Ideally matches Mongo track.
            # Try to find track by ac_id (Type safe)
            track_doc = db.tracks.find_one({"azuracast_id": ac_id})
            if not track_doc:
                track_doc = db.tracks.find_one({"azuracast_id": str(ac_id)})
            
            # Fallback: Title/Artist Match
            if not track_doc and title:
                # Basic fuzzy cleanup for matching
                artist = t.get('artist', '')
                track_doc = db.tracks.find_one({
                    "metadata.title": title,
                    "metadata.artist": artist
                })

            if track_doc:
                song_id = track_doc.get("song_id")
                
                # HEALING: Sync AzuraCast ID if missing/mismatched
                current_ac_id = track_doc.get("azuracast_id")
                if str(current_ac_id) != str(ac_id):
                    try:
                        db.tracks.update_one(
                            {"_id": track_doc["_id"]},
                            {"$set": {"azuracast_id": ac_id}}
                        )
                        if debug_limit > 0:
                            print(f"DEBUG: Linked AC_ID {ac_id} to Song {song_id}")
                    except Exception as e:
                        logger.error(f"Failed to link ID: {e}")

                # Insert Mood
                # Avoid duplicates
                existing = db.moods.find_one({"song_id": song_id, "mood": mood})
                if not existing:
                    db.moods.insert_one({
                        "song_id": song_id,
                        "mood": mood,
                        "source": "import_genre",
                        "timestamp": 1234567890
                    })
                    imported_count += 1
                    if imported_count % 50 == 0:
                        logger.info(f"Imported {imported_count} mood tags...")
            else:
                 if debug_limit > 0:
                     logger.warning(f"No DB match for AC_ID: {ac_id} ({title})")

    logger.info(f"Import Complete. Added {imported_count} mood tags.")

if __name__ == "__main__":
    main()
