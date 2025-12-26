import logging
# from typing import Optional
# from .mongo_client import MongoClient
# from .azuracast_client import AzuraCastClient

logger = logging.getLogger(__name__)

# Mapping: Frontend Vibe -> Backend Playlist Config
MOOD_PLAYLIST_MAP = {
    "energy": "High Voltage",
    "chill": "Slow Burn",
    "groove": "Pocket Logic",
    "dark": "Nocturnals",
    "euphoric": "Starlight",
    # Aliases
    "energetic": "High Voltage",
    "warm": "Slow Burn",
    "groovy": "Pocket Logic"
}

THRESHOLD_VOTES = 3

class LibraryManager:
    """
    Manages the 'Intelligent' part of the library.
    Promotes tracks to curated playlists based on user votes.
    """
    
    def __init__(self, mongo_client, azura_client):
        self.mongo = mongo_client
        self.azura = azura_client
        
    def check_promotion(self, song_id: str):
        """
        Checks if a song qualifies for any mood playlist promotion.
        Should be called after a vote is cast.
        """
        if not self.mongo or not self.azura:
            return

        try:
            # 1. Get all mood votes for this song
            # We need a method in mongo_client to get granular votes
            # For now, let's assume we can aggregage or get raw count.
            # Using existing 'get_song_moods' might give us the totals.
            
            mood_data = self.mongo.get_song_moods(song_id)
            # Structure expected: {'top_mood': 'energy', 'moods': {'energy': 5, 'chill': 1}}
            
            if not mood_data or 'mood_counts' not in mood_data:
                return

            vote_counts = mood_data['mood_counts']
            
            for mood, count in vote_counts.items():
                if count >= THRESHOLD_VOTES:
                    self._promote_song(song_id, mood)
                    
        except Exception as e:
            logger.error(f"Error checking promotion for {song_id}: {e}")

    def _promote_song(self, song_id: str, mood: str):
        """
        Promotes a single song to the target playlist if eligible.
        """
        target_playlist = MOOD_PLAYLIST_MAP.get(mood.lower())
        if not target_playlist:
            return # No curated playlist for this mood

        logger.info(f"⚖️ Checking promotion for {song_id} -> {target_playlist} (Mood: {mood})")
        
        # We assume AzuraCast client handles "Idempotency" (not adding duplicate if already there)
        # OR we just fire and forget, AzuraCast usually ignores dups or handles it.
        # But `add_to_playlist` implementation in azuracast_client uses valid API.
        
        # Converting song_id (str) to int for AzuraCast
        # Converting song_id (str) to int for AzuraCast?
        # AzuraCast Batch API accepts unique_id (string) or media_id (int).
        # We try passing the ID as is (likely a unique_id hash).
        
        try:
            # Check if it looks like an int, try to convert, else pass string
            media_id = song_id
            if str(song_id).isdigit():
                media_id = int(song_id)
            
            # Pass to client (which handles payload)
            success = self.azura.add_to_playlist(media_id, target_playlist)
            if success:
                 logger.info(f"🚀 PROMOTED {media_id} to '{target_playlist}'!")
        except Exception as e:
            logger.error(f"Error promoting song {song_id}: {e}")
