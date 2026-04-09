from typing import List, Dict, Any
from music_scanner import MusicScanner
from tag_improver import TagImprover

class AppState:
    def __init__(self):
        self.library: List[Dict[str, Any]] = []
        self.scanner = MusicScanner()
        self.tag_improver = TagImprover()
        self.organizer = None 
        self.scan_path = ""
        self.mongo_client = None
        self.track_matcher = None
        self.library_service = None
        self.azura_client = None # Global AzuraCast Client
        self.library_manager = None # Auto-Curation Manager
        
        # Per-Station Data
        self.now_playing: Dict[int, Dict[str, Any]] = {}
        self.steering_status: Dict[int, Dict[str, Any]] = {}
        self.voting_session: Dict[int, Dict[str, Any]] = {}
        self.stream_urls: Dict[int, str] = {}
        
        # Initialize defaults for known stations
        for sid in [1, 2]:
            self.now_playing[sid] = {
                "title": "Station Online",
                "artist": "YourParty Radio",
                "album": "",
                "art": "https://radio.yourparty.tech/wp-content/uploads/2023/11/station_logo.png",
                "id": "init",
                "duration": 0
            }
            self.steering_status[sid] = {"mode": "auto", "target": None, "updated_at": None}
            self.voting_session[sid] = {"candidates": [], "expires_at": None}
            self.stream_urls[sid] = f"https://radio.yourparty.tech/radio{sid if sid > 1 else ''}.mp3"

state = AppState()

def get_state():
    return state
