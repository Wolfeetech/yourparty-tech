from typing import Optional, List
from pydantic import BaseModel

# ========== CONSTANTS ==========
VALID_MOODS = [
    "energy", "chill", "groove", "dark", "euphoric",
    "melancholic", "hypnotic", "aggressive", "trippy", "warm",
    "driving", "acid", "soulful", "deep", "funky", 
    "uplifting", "progressive", "psy", "classic", "energetic"
]

# ========== MODELS ==========

class ScanRequest(BaseModel):
    path: str

class OrganizeRequest(BaseModel):
    dry_run: bool = True
    output_path: Optional[str] = None # Optional SMB/Network path

class TagImproveRequest(BaseModel):
    file_path: str

class AzuraCastSyncRequest(BaseModel):
    base_url: str
    api_key: str
    station_id: int

class MongoConfigRequest(BaseModel):
    connection_string: str = "mongodb://localhost:27017/"
    database_name: str = "radio_ratings"

class RatingRequest(BaseModel):
    song_id: str
    rating: int
    user_id: str = "anonymous"
    file_path: Optional[str] = None
    title: Optional[str] = None
    artist: Optional[str] = None
    station_id: int = 1

class MoodRequest(BaseModel):
    song_id: str
    mood: Optional[str] = None
    genre: Optional[str] = None
    keyword: Optional[str] = None
    title: Optional[str] = None
    artist: Optional[str] = None
    station_id: int = 1

class MoodVoteRequest(BaseModel):
    """Request model for dual mood voting (current + next)."""
    song_id: str
    mood_current: Optional[str] = None  # What mood IS this song?
    mood_next: Optional[str] = None     # What mood do you WANT next?
    rating: Optional[int] = None        # 1-5 star rating
    vote: Optional[str] = None          # like/dislike
    user_id: str = "anonymous"
    station_id: int = 1

class MoodNextVoteRequest(BaseModel):
    """Specific request for voting on the NEXT mood only."""
    song_id: str
    mood_next: str
    station_id: int = 1

class TrackVoteRequest(BaseModel):
    """Request for specific track voting (MTV style)."""
    track_id: str
    user_id: str = "anonymous"
    station_id: int = 1

class VoteNextRequest(BaseModel):
    """Simple vote request."""
    vote: str
    station_id: int = 1

class SteeringRequest(BaseModel):
    mode: str = "auto"  # 'auto', 'manual', 'off'
    target: Optional[str] = None
    station_id: int = 1

class ShoutoutRequest(BaseModel):
    message: str
    sender: str = "Anonymous"
    user_id: str = "anonymous"
    station_id: int = 1

