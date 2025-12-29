
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("PlaylistService")

class PlaylistService:
    def __init__(self, mongo_client, azura_client):
        self.mongo = mongo_client
        self.azura = azura_client
        
        # Configuration: Playlist Name mapped to Mongo Mood Query
        self.playlist_rules = [
            {
                "name": "Starlight", 
                "mood": "Euphoric", 
                "min_rating": 4.0,
                "description": "Euphoric & High Energy Tracks"
            },
            {
                "name": "Slow Burn", 
                "mood": "Chill", 
                "min_rating": 0.0,
                "description": "Relaxed & Deep Vibes"
            },
            {
                "name": "Power Hour", 
                "mood": "Energy", 
                "min_rating": 3.0,
                "description": "High Intensity Workout"
            }
        ]

    async def sync_all_playlists(self) -> List[Dict[str, Any]]:
        """
        Sync all configured playlists from MongoDB to AzuraCast.
        """
        results = []
        for rule in self.playlist_rules:
            res = await self.sync_playlist(rule['name'], rule['mood'], rule['min_rating'])
            results.append(res)
        return results

    async def sync_playlist(self, name: str, mood: str, min_rating: float) -> Dict[str, Any]:
        """
        1. Query Mongo for tracks with matching mood.
        2. Extract AzuraCast Media IDs.
        3. Push to AzuraCast Playlist.
        """
        if not self.mongo or not self.azura:
            return {"playlist": name, "success": False, "error": "Clients not initialized"}
            
        try:
            # 1. Get IDs from Mongo
            # This uses the method we added to mongo_client.py
            media_ids = self.mongo.get_tracks_for_playlist(mood=mood, min_rating=min_rating)
            
            if not media_ids:
                return {
                    "playlist": name, 
                    "success": True, 
                    "count": 0, 
                    "message": "No matching tracks found (or no AzuraCast IDs linked)"
                }
            
            # 2. Add to AzuraCast Playlist
            # Check if playlist exists, create if not
            playlists = await self.azura.get_playlists()
            target_pl = next((p for p in playlists if p['name'].lower() == name.lower()), None)
            
            if not target_pl:
                logger.info(f"Creating missing playlist: {name}")
                target_pl = await self.azura.create_playlist(name)
                
            if target_pl:
                pl_id = target_pl['id']
                # Replace content
                success = await self.azura.replace_playlist_content(pl_id, media_ids)
                
                return {
                    "playlist": name,
                    "success": success,
                    "count": len(media_ids),
                    "media_ids": media_ids[:5] # Sample
                }
            else:
                return {"playlist": name, "success": False, "error": "Could not create playlist"}
                
        except Exception as e:
            logger.error(f"Failed to sync playlist {name}: {e}")
            return {"playlist": name, "success": False, "error": str(e)}

    def get_rules(self):
        return self.playlist_rules
