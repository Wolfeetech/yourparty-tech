import logging
import os
from typing import Dict, Any, Optional, List
from pymongo import MongoClient
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== GAMIFICATION CONFIG ==========
POINTS_CONFIG = {
    "mood_vote": 10,           # Points for voting on current track mood
    "mood_next_vote": 5,       # Points for voting on next mood
    "rating": 15,              # Points for rating a track
    "discovery_tag": 25,       # Bonus for tagging an untagged track
    "streak_bonus_per_day": 5, # Extra points per day streak
    "streak_max_bonus": 50     # Maximum streak bonus
}

class MongoDatabaseClient:
    """
    Client for MongoDB integration - handles ratings, metadata, and sync with library.
    """
    def __init__(self, connection_string: str = None, database_name: str = None):
        """
        Initialize MongoDB client.
        
        Args:
            connection_string: MongoDB connection string (default: env MONGO_URI)
            database_name: Override database name (default: extracted from URI or 'yourparty')
        """
        try:
            self.client = MongoClient(connection_string)
            
            # Extract database from URI if not explicitly provided
            if database_name:
                self.db = self.client[database_name]
            else:
                # Try to get default database from URI
                self.db = self.client.get_default_database(default="yourparty")
            
            self.ratings_collection = self.db["rating_events"]
            self.tracks_collection = self.db["tracks"]
            self.sync_log_collection = self.db["sync_log"]
            self.moods_collection = self.db["moods"]
            self.mood_next_votes_collection = self.db["mood_next_votes"]
            self.shoutouts_collection = self.db["shoutouts"]

            # Configure timeouts to prevent hanging
            # If these are not set, it can hang for 30s+ which systemd might kill
            # serverSelectionTimeoutMS=5000 (5s)
            
            if connection_string:
               if 'serverSelectionTimeoutMS' not in connection_string:
                   # Re-init with explicit timeout if not in URI
                   self.client = MongoClient(connection_string, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000)
            
            # Configure indexing
            try:
                self.ratings_collection.create_index("song_id")
                self.ratings_collection.create_index("user_id")
                
                # Use relative_path for cross-platform consistency (SSOT requirement)
                # Partial index avoids duplicate nulls during backfills/migrations.
                self.tracks_collection.create_index(
                    "relative_path",
                    unique=True,
                    partialFilterExpression={"relative_path": {"$type": "string"}},
                )
                self.tracks_collection.create_index("file_path") # Legacy support
                self.tracks_collection.create_index("song_id")
                
                # Metadata indexes for Audio Science
                self.tracks_collection.create_index("metadata.initial_key")
                self.tracks_collection.create_index("metadata.bpm")
            except Exception as ie:
                logger.warning(f"Index creation warning: {ie}")
            
            logger.info(f"Connected to MongoDB: {database_name}")
        except Exception as e:
            # Only fail on connection errors, not index errors
            logger.error(f"MongoDB connection failed: {e}")
            raise

    def normalize_path(self, full_path: str) -> str:
        """
        Converts absolute Windows/Linux paths to a relative path from the library root.
        E.g., 'Z:\\yourparty_Libary\\Rock\\Artist\\Song.mp3' -> 'Rock/Artist/Song.mp3'
        """
        library_subdir = os.getenv("LIBRARY_SUBDIR", "yourparty_Libary")
        library_root_win = os.getenv("LIBRARY_ROOT_WIN", rf"Z:\{library_subdir}")
        library_root_linux = os.getenv(
            "LIBRARY_ROOT_LINUX",
            f"/var/radio/music/{library_subdir}"
        )
        library_unc = os.getenv(
            "LIBRARY_UNC",
            rf"\\192.168.178.25\music\{library_subdir}"
        )

        # Common library roots (new + legacy fallbacks)
        roots = [
            library_root_win,
            library_root_linux,
            library_unc,
            "Z:/radio_library",
            r"Z:\radio_library",
            r"M:\Library",
            "/var/azuracast/stations/yourparty/media",
            "/var/azuracast/stations/radio4yourparty/media",
            f"/var/azuracast/music_storage/{library_subdir}",
            "/var/azuracast/music_storage",
            "/var/radio/music",
            "/mnt/music_hdd",
        ]
        
        normalized = full_path.replace("\\", "/")
        normalized_roots = [
            r.replace("\\", "/").rstrip("/") + "/"
            for r in roots
            if r
        ]
        for root_norm in normalized_roots:
            if normalized.lower().startswith(root_norm.lower()):
                return normalized[len(root_norm):].strip("/")
        
        # If no root match, return the basename
        return normalized.split("/")[-1]

    def get_track_rating(self, file_path: str = None, song_id: str = None, station_id: int = 1) -> Optional[Dict[str, Any]]:
        """
        Get aggregated rating for a track.
        
        Args:
            file_path: Local file path
            song_id: AzuraCast song ID
            station_id: Station identifier
        
        Returns:
            Dict with rating statistics or None
        """
        try:
            query = {}
            if station_id:
                query["station_id"] = station_id
            if song_id:
                query["song_id"] = song_id
            elif file_path:
                # First find the track to get its song_id
                track = self.tracks_collection.find_one({"file_path": file_path})
                if track and "song_id" in track:
                    query["song_id"] = track["song_id"]
                else:
                    return None
            else:
                return None
            
            # Aggregate ratings
            pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": "$song_id",
                    "average": {"$avg": "$rating"},
                    "total": {"$sum": 1},
                    "distribution": {
                        "$push": "$rating"
                    }
                }}
            ]
            
            result = list(self.ratings_collection.aggregate(pipeline))
            if result:
                data = result[0]
                # Count distribution
                dist = {}
                for rating in data["distribution"]:
                    dist[str(rating)] = dist.get(str(rating), 0) + 1
                
                return {
                    "average": round(data["average"], 2),
                    "total": data["total"],
                    "distribution": dist
                }
            return None
        except Exception as e:
            logger.error(f"Error fetching rating: {e}")
            return None

    def submit_rating(self, song_id: str, rating: int, user_id: str = "anonymous", 
                     file_path: str = None, station_id: int = 1, **kwargs) -> Dict[str, Any]:
        """
        Submit a new rating for a track.
        
        Args:
            song_id: AzuraCast song ID
            rating: Rating value (1-5)
            user_id: User identifier
            station_id: Station identifier
            file_path: Optional local file path for tracking
        
        Returns:
            Dict with success status and updated ratings
        """
        try:
            if rating < 1 or rating > 5:
                return {"success": False, "error": "Rating must be between 1 and 5"}
            
            rating_doc = {
                "song_id": song_id,
                "rating": rating,
                "user_id": user_id,
                "station_id": station_id,
                "timestamp": datetime.utcnow(),
                "file_path": file_path
            }
            
            # Insert rating
            self.ratings_collection.insert_one(rating_doc)
            
            # Save metadata if provided (Fix for "Unknown" tracks)
            if "metadata" in kwargs and kwargs["metadata"]:
                 self.save_song_metadata(song_id, kwargs["metadata"])
            
            # Update or create track document
            if file_path:
                self.tracks_collection.update_one(
                    {"file_path": file_path},
                    {"$set": {
                        "song_id": song_id,
                        "last_rated": datetime.utcnow()
                    }},
                    upsert=True
                )
            
            # Return updated rating stats
            updated_ratings = self.get_track_rating(song_id=song_id)
            
            return {
                "success": True,
                "ratings": updated_ratings
            }
        except Exception as e:
            logger.error(f"Error submitting rating: {e}")
            return {"success": False, "error": str(e)}

    def submit_vote(self, song_id: str, vote: str, user_id: str = "anonymous", station_id: int = 1) -> Dict[str, int]:
        """
        Submit a boolean vote (like/dislike) and return updated counts.
        """
        try:
            if not hasattr(self, 'votes_collection'):
                self.votes_collection = self.db["votes"]
                self.votes_collection.create_index("song_id")

            vote_doc = {
                "song_id": song_id,
                "vote": vote, # 'like' or 'dislike'
                "user_id": user_id,
                "timestamp": datetime.utcnow()
            }
            self.votes_collection.insert_one(vote_doc)
            
            # Aggregate counts
            pipeline = [
                {"$match": {"song_id": song_id, "station_id": station_id}},
                {"$group": {"_id": "$vote", "count": {"$sum": 1}}}
            ]
            results = list(self.votes_collection.aggregate(pipeline))
            counts = {r["_id"]: r["count"] for r in results}
            
            return counts
        except Exception as e:
            logger.error(f"Error submitting vote: {e}")
            return {}

    def submit_mood(self, song_id: str, mood: str = None, genre: str = None, user_id: str = "anonymous", station_id: int = 1, **kwargs) -> Dict[str, Any]:
        """
        Submit a new mood or genre tag for a track.
        """
        try:
            doc = {
                "song_id": song_id,
                "user_id": user_id,
                "station_id": station_id,
                "timestamp": datetime.utcnow()
            }
            if mood:
                doc['mood'] = mood
            if genre:
                doc['genre'] = genre
            
            # Use a separate collection for moods, or just log it
            # For simplicity, let's assume a 'moods' collection
            if not hasattr(self, 'moods_collection'):
                 self.moods_collection = self.db["moods"]
                 self.moods_collection.create_index("song_id")

            self.moods_collection.insert_one(doc)
            
            # Save metadata if provided
            if "metadata" in kwargs and kwargs["metadata"]:
                 self.save_song_metadata(song_id, kwargs["metadata"])

            return {"success": True, "tag": mood or genre, "message": "Tag saved!"}
        except Exception as e:
            logger.error(f"Error submitting mood: {e}")
            return {"success": False, "error": str(e)}

    def get_all_moods(self) -> Dict[str, Any]:
        """Aggregate top moods for all songs."""
        try:
            if not hasattr(self, 'moods_collection'):
                 self.moods_collection = self.db["moods"]
                 
            pipeline = [
                {"$group": {"_id": "$mood", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            
            results = list(self.moods_collection.aggregate(pipeline))
            return {
                "top_moods": [{"tag": r["_id"], "count": r["count"]} for r in results if r["_id"]]
            }
        except Exception as e:
            logger.error(f"Error fetching mood stats: {e}")
            return {}

    def save_song_metadata(self, song_id: str, metadata: Dict[str, Any]) -> bool:
        """Upsert metadata for a song_id (Title, Artist, Cover)."""
        try:
            self.db["song_metadata"].update_one(
                {"song_id": song_id},
                {"$set": {
                    "metadata": metadata,
                    "updated_at": datetime.utcnow()
                }},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
            return False

    def get_song_metadata(self, song_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve metadata for a song."""
        try:
            doc = self.db["song_metadata"].find_one({"song_id": song_id})
            return doc.get("metadata") if doc else None
        except Exception:
            return None

    def get_random_tracks(self, limit: int = 3) -> List[Dict[str, Any]]:
        """Get random tracks with metadata from song_metadata collection."""
        try:
             # Sample random tracks that have metadata
             pipeline = [
                 {"$match": {"metadata.title": {"$exists": True}}},
                 {"$sample": {"size": limit}}
             ]
             return list(self.db["song_metadata"].aggregate(pipeline))
        except Exception as e:
            logger.error(f"Error getting random tracks: {e}")
            return []

    def get_song_moods(self, song_id: str) -> Dict[str, Any]:
        """Get mood tags for a specific song with counts."""
        try:
            if not hasattr(self, 'moods_collection'):
                 self.moods_collection = self.db["moods"]
            
            # Get all mood counts for this song
            pipeline = [
                {"$match": {"song_id": song_id}},
                {"$group": {"_id": "$mood", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            
            results = list(self.moods_collection.aggregate(pipeline))
            
            mood_counts = {}
            top_mood = None
            for r in results:
                if r["_id"]:
                    mood_counts[r["_id"]] = r["count"]
                    if top_mood is None:
                        top_mood = r["_id"]
                
            return {
                "top_mood": top_mood,
                "mood_counts": mood_counts,
                "all_moods": [r["_id"] for r in results if r["_id"]]
            }
        except Exception as e:
            logger.error(f"Error getting song moods: {e}")
            return {"top_mood": None, "mood_counts": {}}

    # ========== MOOD VOTING SYSTEM ==========
    
    def submit_mood_next_vote(self, song_id: str, mood_next: str, user_id: str = "anonymous", station_id: int = 1) -> Dict[str, Any]:
        """
        Store a user's preference for what mood they want next.
        Used by the auto-DJ to influence track selection.
        
        Args:
            song_id: Current song ID (for context)
            mood_next: Desired mood for next track
            user_id: User identifier
            station_id: Station identifier
        """
        try:
            if not hasattr(self, 'mood_next_votes_collection'):
                self.mood_next_votes_collection = self.db["mood_next_votes"]
                self.mood_next_votes_collection.create_index("timestamp")
                self.mood_next_votes_collection.create_index("mood_next")
                self.mood_next_votes_collection.create_index("station_id")
            
            vote_doc = {
                "song_id": song_id,  # What was playing when vote was cast
                "mood_next": mood_next,
                "user_id": user_id,
                "station_id": station_id,
                "timestamp": datetime.utcnow()
            }
            
            self.mood_next_votes_collection.insert_one(vote_doc)
            logger.info(f"Mood next vote stored for station {station_id}: {mood_next}")
            
            # Recalculate dominant mood for immediate feedback
            dominant = self.get_dominant_next_mood(time_window_minutes=30, station_id=station_id)
            
            return {
                "success": True, 
                "mood_next": mood_next, 
                "dominant_next": dominant
            }
        except Exception as e:
            logger.error(f"Error submitting mood_next vote: {e}")
            return {"success": False, "error": str(e)}
    
    def get_track_metadata(self, song_id: str) -> Dict[str, Any]:
        """
        Get basic metadata (Key, BPM) for a track by Song ID.
        """
        try:
            track = self.tracks_collection.find_one({"song_id": song_id}, {"metadata": 1})
            if track and "metadata" in track:
                return {
                    "initial_key": track["metadata"].get("initial_key"),
                    "bpm": track["metadata"].get("bpm")
                }
            return {}
        except Exception as e:
            logger.error(f"Error fetching track metadata for {song_id}: {e}")
            return {}

    def get_dominant_next_mood(self, time_window_minutes: int = 10, station_id: int = 1) -> Optional[str]:
        """
        Get the dominant mood preference from recent votes.
        Used by auto-DJ to select the next track.
        
        Args:
            time_window_minutes: How far back to look for votes
            station_id: Station identifier
            
        Returns:
            Most voted mood in the time window, or None
        """
        try:
            if not hasattr(self, 'mood_next_votes_collection'):
                self.mood_next_votes_collection = self.db["mood_next_votes"]
            
            from datetime import timedelta
            cutoff = datetime.utcnow() - timedelta(minutes=time_window_minutes)
            
            pipeline = [
                {"$match": {
                    "timestamp": {"$gte": cutoff},
                    "station_id": station_id
                }},
                {"$group": {"_id": "$mood_next", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 1}
            ]
            
            results = list(self.mood_next_votes_collection.aggregate(pipeline))
            
            if results and results[0]["_id"]:
                logger.info(f"Dominant next mood for station {station_id}: {results[0]['_id']} ({results[0]['count']} votes)")
                return results[0]["_id"]
            
            return None
        except Exception as e:
            logger.error(f"Error getting dominant next mood: {e}")
            return None
    
    def get_tracks_by_mood(self, mood: str, limit: int = 50, station_id: Optional[int] = None, allowed_keys: List[str] = None) -> List[Dict[str, Any]]:
        """
        Get tracks tagged with a specific mood, optionally filtering by Harmonic Key.
        Used for auto-DJ track selection.
        
        Args:
            mood: Target mood
            limit: Maximum tracks to return
            station_id: Optional station identifier to filter votes
            allowed_keys: List of allowed Camelot keys (e.g. ['8A', '9A'])
            
        Returns:
            List of track documents with that mood
        """
        try:
            if not hasattr(self, 'moods_collection'):
                self.moods_collection = self.db["moods"]
            
            query = {"mood": mood}
            if station_id is not None:
                query["station_id"] = station_id

            # Get all song_ids with this mood
            # Fetch more if we are filtering by key to ensure we find enough matches
            fetch_limit = limit * 4 if allowed_keys else limit * 2
            
            mood_docs = list(self.moods_collection.find(
                query,
                {"song_id": 1}
            ).limit(fetch_limit))
            
            song_ids = list(set(doc["song_id"] for doc in mood_docs if doc.get("song_id")))
            
            # Enrich with track metadata and filter by key
            tracks = []
            for song_id in song_ids:
                if len(tracks) >= limit:
                    break
                    
                track_query = {"song_id": song_id}
                if allowed_keys:
                    track_query["metadata.initial_key"] = {"$in": allowed_keys}
                
                track = self.tracks_collection.find_one(track_query)
                if track:
                    tracks.append({
                        "song_id": song_id,
                        "file_path": track.get("file_path"),
                        "metadata": track.get("metadata", {}),
                        "mood": mood
                    })
            
            logger.info(f"Found {len(tracks)} tracks with mood: {mood} (Keys: {allowed_keys if allowed_keys else 'All'})")
            return tracks
        except Exception as e:
            logger.error(f"Error getting tracks by mood: {e}")
            return []

    def get_tracks_for_playlist(self, mood: str = None, min_rating: float = 0, limit: int = 500) -> List[int]:
        """
        Get AzuraCast Media IDs for tracks matching criteria.
        Used for checking playlist syncing.
        """
        try:
            query = {}
            if mood:
                # Query mood directly on tracks (V2 fix)
                query["mood"] = mood
            
            # Add Rating Filter (Complex because rating is aggregated)
            # For simplicity in V1, we just filter by mood and existence of azuracast_id
            # If min_rating > 0, we might need a join or pre-aggregation.
            # Let's trust the mood tag for now, or filter in Python if list is small.
            
            query["azuracast_id"] = {"$exists": True, "$ne": None}
            
            tracks = list(self.tracks_collection.find(query, {"azuracast_id": 1}).limit(limit))
            return [int(t["azuracast_id"]) for t in tracks if t.get("azuracast_id")]
        except Exception as e:
            logger.error(f"Error getting playlist tracks: {e}")
            return []

    # ========== NEXT TRACK VOTING ==========

    def submit_next_track_vote(self, candidate_song_id: str, user_id: str = "anonymous", station_id: int = 1) -> bool:
        """Vote for a specific track to play next."""
        try:
            if not hasattr(self, 'next_track_votes_collection'):
                self.next_track_votes_collection = self.db["next_track_votes"]
                self.next_track_votes_collection.create_index("candidate_song_id")
                self.next_track_votes_collection.create_index("timestamp")
                self.next_track_votes_collection.create_index("station_id")
            
            # Simple vote document
            self.next_track_votes_collection.insert_one({
                "candidate_song_id": candidate_song_id,
                "user_id": user_id,
                "station_id": station_id,
                "timestamp": datetime.utcnow()
            })
            return True
        except Exception as e:
            logger.error(f"Error submitting next track vote: {e}")
            return False

    def get_next_track_vote_counts(self, candidate_ids: List[str]) -> Dict[str, int]:
        """Get vote counts for specific candidates in the last 15 minutes."""
        try:
            if not hasattr(self, 'next_track_votes_collection'):
                 return {cid: 0 for cid in candidate_ids}

            # Only count recent votes (current voting window)
            cutoff = datetime.utcnow() - timedelta(minutes=10)
            
            pipeline = [
                {"$match": {
                    "candidate_song_id": {"$in": candidate_ids},
                    "timestamp": {"$gte": cutoff}
                }},
                {"$group": {"_id": "$candidate_song_id", "count": {"$sum": 1}}}
            ]
            
            results = list(self.next_track_votes_collection.aggregate(pipeline))
            counts = {r["_id"]: r["count"] for r in results}
            
            # Ensure all requested IDs are present
            return {cid: counts.get(cid, 0) for cid in candidate_ids}
        except Exception as e:
            logger.error(f"Error getting next track vote counts: {e}")
            return {cid: 0 for cid in candidate_ids}

    def get_top_voted_track(self, time_window_minutes: int = 15, station_id: int = 1) -> Optional[str]:
        """Get the song_id with the most votes in the window."""
        try:
            if not hasattr(self, 'next_track_votes_collection'):
                self.next_track_votes_collection = self.db["next_track_votes"]
            
            cutoff = datetime.utcnow() - timedelta(minutes=time_window_minutes)
            pipeline = [
                {"$match": {
                    "timestamp": {"$gte": cutoff},
                    "station_id": station_id
                }},
                {"$group": {"_id": "$candidate_song_id", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 1}
            ]
            
            results = list(self.next_track_votes_collection.aggregate(pipeline))
            if results and results[0]["_id"]:
                logger.info(f"Top voted track for station {station_id}: {results[0]['_id']} ({results[0]['count']} votes)")
                return results[0]["_id"]
            return None
        except Exception as e:
            logger.error(f"Error getting top voted track: {e}")
            return None

    # ========== PLAYTIME MODE QUERIES ==========
    
    def get_untagged_tracks(self, genres: List[str] = None, limit: int = 50, station_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        DISCOVERY MODE: Get tracks with no/few mood votes for tagging.
        
        Args:
            genres: Optional list of genres to filter by
            limit: Maximum tracks to return
            station_id: Optional station identifier to filter votes
            
        Returns:
            List of tracks needing mood tags
        """
        try:
            if not hasattr(self, 'moods_collection'):
                self.moods_collection = self.db["moods"]
            
            # Get all song_ids that have mood entries
            mood_filter = {"station_id": station_id} if station_id is not None else {}
            tagged_song_ids = self.moods_collection.distinct("song_id", mood_filter)
            
            # Query for tracks NOT in the tagged list
            query = {"song_id": {"$nin": list(tagged_song_ids)}}
            
            # Optional genre filter
            if genres:
                query["$or"] = [
                    {"metadata.genre": {"$in": genres}},
                    {"file_path": {"$regex": "|".join(genres), "$options": "i"}}
                ]
            
            tracks = list(self.tracks_collection.find(query).limit(limit))
            
            result = []
            for track in tracks:
                result.append({
                    "song_id": track.get("song_id"),
                    "file_path": track.get("file_path"),
                    "metadata": track.get("metadata", {}),
                    "mode": "discovery"
                })
            
            logger.info(f"[DISCOVERY] Found {len(result)} untagged tracks")
            return result
        except Exception as e:
            logger.error(f"Error getting untagged tracks: {e}")
            return []
    
    def get_tagged_tracks(self, limit: int = 50, station_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get tracks that have at least one mood tag.
        
        Args:
            limit: Maximum tracks to return
            station_id: Optional station identifier to filter votes
            
        Returns:
            List of tagged tracks
        """
        try:
            if not hasattr(self, 'moods_collection'):
                self.moods_collection = self.db["moods"]
            
            # Get distinct song_ids with mood tags
            mood_filter = {"station_id": station_id} if station_id is not None else {}
            tagged_song_ids = list(self.moods_collection.distinct("song_id", mood_filter))[:limit]
            
            result = []
            for song_id in tagged_song_ids:
                track = self.tracks_collection.find_one({"song_id": song_id})
                if track:
                    mood_data = self.get_song_moods(song_id)
                    result.append({
                        "song_id": song_id,
                        "file_path": track.get("file_path"),
                        "metadata": track.get("metadata", {}),
                        "top_mood": mood_data.get("top_mood"),
                        "mood_counts": mood_data.get("mood_counts", {}),
                        "mode": "refinement"
                    })
            
            logger.info(f"[REFINEMENT] Found {len(result)} tagged tracks")
            return result
        except Exception as e:
            logger.error(f"Error getting tagged tracks: {e}")
            return []
    
    def get_tracks_needing_refinement(
        self,
        min_votes: int = 1,
        max_votes: int = 10,
        limit: int = 30,
        station_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        REFINEMENT MODE: Get tracks with some tags but needing more verification.
        """
        try:
            if not hasattr(self, 'moods_collection'):
                self.moods_collection = self.db["moods"]
            
            # Aggregate to find song_ids with vote counts in range
            pipeline = []
            if station_id is not None:
                pipeline.append({"$match": {"station_id": station_id}})
            pipeline += [
                {"$group": {"_id": "$song_id", "vote_count": {"$sum": 1}}},
                {"$match": {"vote_count": {"$gte": min_votes, "$lte": max_votes}}},
                {"$sort": {"vote_count": 1}},  # Prioritize lowest vote counts
                {"$limit": limit}
            ]
            
            song_stats = list(self.moods_collection.aggregate(pipeline))
            
            result = []
            for stat in song_stats:
                song_id = stat["_id"]
                if not song_id:
                    continue
                    
                track = self.tracks_collection.find_one({"song_id": song_id})
                if track:
                    mood_data = self.get_song_moods(song_id)
                    result.append({
                        "song_id": song_id,
                        "file_path": track.get("file_path"),
                        "metadata": track.get("metadata", {}),
                        "vote_count": stat["vote_count"],
                        "top_mood": mood_data.get("top_mood"),
                        "mood_counts": mood_data.get("mood_counts", {}),
                        "mode": "refinement"
                    })
            
            logger.info(f"[REFINEMENT] Found {len(result)} tracks needing more votes")
            return result
        except Exception as e:
            logger.error(f"Error getting tracks needing refinement: {e}")
            return []

    # ========== PLAYLIST CACHING (Decoupling) ==========

    def save_playlists(self, playlists: List[Dict[str, Any]]) -> bool:
        """
        Cache full playlist objects from AzuraCast to MongoDB.
        Replaces the entire collection or uses upsert (we'll replace for simplicity/cleanliness).
        """
        try:
            if not hasattr(self, 'playlists_collection'):
                self.playlists_collection = self.db["playlists"]
            
            # Timestamp for sync tracking
            sync_time = datetime.utcnow()
            
            # Prepare docs
            docs = []
            for pl in playlists:
                pl['last_synced'] = sync_time
                docs.append(pl)
                
            if not docs:
                return True
                
            # Bulk write or Drop/Insert?
            # Safe strategy: Update each by ID, remove stale ones later?
            # Or simpler: Drop collection and rewrite (fastest for small datasets <100 playlists)
            # Let's use update_one upsert to be safe against concurrency quirks
            
            ids_processed = []
            for doc in docs:
                self.playlists_collection.update_one(
                    {"id": doc["id"]},
                    {"$set": doc},
                    upsert=True
                )
                ids_processed.append(doc["id"])
                
            # Optional: Remove playlists not in the new list (deleted on AzuraCast)
            self.playlists_collection.delete_many({"id": {"$nin": ids_processed}})
            
            logger.info(f"Synced {len(docs)} playlists to MongoDB cache")
            return True
        except Exception as e:
            logger.error(f"Error caching playlists: {e}")
            return False

    def get_cached_playlists(self) -> List[Dict[str, Any]]:
        """Retrieve playlists from local cache (Instant Read)."""
        try:
            if not hasattr(self, 'playlists_collection'):
                self.playlists_collection = self.db["playlists"]
                
            return list(self.playlists_collection.find({}, {"_id": 0}))
        except Exception as e:
            logger.error(f"Error reading cached playlists: {e}")
            return []



    def sync_track_metadata(self, file_path: str, metadata: Dict[str, Any], song_id: str = None):
        """
        Sync improved metadata to MongoDB.
        
        Args:
            file_path: Local file path
            metadata: Metadata dict from tag_improver
            song_id: Optional AzuraCast song ID
        """
        try:
            track_doc = {
                "file_path": file_path,
                "metadata": metadata,
                "last_updated": datetime.utcnow()
            }
            
            if song_id:
                track_doc["song_id"] = song_id
            
            self.tracks_collection.update_one(
                {"file_path": file_path},
                {"$set": track_doc},
                upsert=True
            )
            
            logger.info(f"Synced metadata for {file_path}")
            return {"success": True}
        except Exception as e:
            logger.error(f"Error syncing metadata: {e}")
            return {"success": False, "error": str(e)}

    def get_all_rated_tracks(self, min_rating: float = 0.0, station_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all tracks with ratings above a threshold.
        """
        try:
            # Aggregate ratings
            pipeline = []
            if station_id is not None:
                pipeline.append({"$match": {"station_id": station_id}})
            pipeline += [
                {"$group": {
                    "_id": "$song_id",
                    "average": {"$avg": "$rating"},
                    "total": {"$sum": 1}
                }},
                {"$match": {"average": {"$gte": min_rating}}},
                {"$sort": {"average": -1}}
            ]
            
            raw_results = list(self.ratings_collection.aggregate(pipeline))
            
            if not raw_results:
                return []

            # Collect IDs for bulk lookup
            song_ids = [r["_id"] for r in raw_results if r["_id"]]
            
            # Lookup 1: Dedicated Song Metadata (The "Unknown Fix")
            # We assume a 'song_metadata' collection exists now
            song_metas = {}
            try:
                cursor = self.db["song_metadata"].find({"song_id": {"$in": song_ids}})
                for doc in cursor:
                    song_metas[doc["song_id"]] = doc.get("metadata", {})
            except Exception:
                pass # Collection might not exist yet

            # Lookup 2: Legacy Track Data (File Paths)
            track_infos = {}
            cursor = self.tracks_collection.find({"song_id": {"$in": song_ids}})
            for doc in cursor:
                track_infos[doc["song_id"]] = doc

            # Merge Data
            result = []
            for rating in raw_results:
                sid = rating["_id"]
                if not sid: continue
                
                # Metadata Priority: SongMetadata (API) > Track (ID3/File) > Filename
                meta_api = song_metas.get(sid, {})
                track_doc = track_infos.get(sid, {})
                meta_track = track_doc.get("metadata", {})
                
                # Merge into final metadata object
                final_meta = {**meta_track, **meta_api} # API overrides track
                
                file_path = track_doc.get("file_path")
                
                # Fallback: Parse Filename if still unknown
                if (not final_meta.get("title") or not final_meta.get("artist")) and file_path:
                    import os
                    filename = os.path.basename(file_path)
                    name_part = os.path.splitext(filename)[0]
                    
                    artist_guess = "Unknown"
                    title_guess = name_part
                    
                    if " - " in name_part:
                        parts = name_part.split(" - ", 1)
                        artist_guess = parts[0]
                        title_guess = parts[1]
                        
                    if not final_meta.get("artist"): final_meta["artist"] = artist_guess
                    if not final_meta.get("title"): final_meta["title"] = title_guess

                result.append({
                    "song_id": sid,
                    "file_path": file_path,
                    "metadata": final_meta,
                    "rating": {
                        "average": round(rating["average"], 2),
                        "total": rating["total"]
                    }
                })
            
            return result
        except Exception as e:
            logger.error(f"Error fetching rated tracks: {e}")
            return []

    def log_sync_operation(self, operation: str, details: Dict[str, Any]):
        """
        Log sync operations for debugging.
        
        Args:
            operation: Operation name (e.g., "library_organized", "azuracast_sync")
            details: Operation details
        """
        try:
            log_doc = {
                "operation": operation,
                "timestamp": datetime.utcnow(),
                "details": details
            }
            self.sync_log_collection.insert_one(log_doc)
        except Exception as e:
            logger.error(f"Error logging sync operation: {e}")

    # ========== GAMIFICATION SYSTEM ==========
    
    def _ensure_gamification_collections(self):
        """Ensure gamification collections exist with proper indexes."""
        if not hasattr(self, 'user_points_collection'):
            self.user_points_collection = self.db["user_points"]
            self.user_points_collection.create_index("user_id", unique=True)
            self.user_points_collection.create_index([("total_points", -1)])  # For leaderboard
    
    def award_points(self, user_id: str, action: str, bonus_multiplier: float = 1.0, song_id: str = None) -> Dict[str, Any]:
        """
        Award points to a user for an action (vote, rating, etc.).
        
        Args:
            user_id: User identifier
            action: Action type from POINTS_CONFIG
            bonus_multiplier: Optional multiplier (e.g., for discovery mode)
            song_id: Optional song context
            
        Returns:
            Updated user stats including points and streak
        """
        try:
            self._ensure_gamification_collections()
            
            base_points = POINTS_CONFIG.get(action, 0)
            points = int(base_points * bonus_multiplier)
            
            # Get current user data
            user_doc = self.user_points_collection.find_one({"user_id": user_id}) or {
                "user_id": user_id,
                "total_points": 0,
                "streak_days": 0,
                "last_activity_date": None,
                "created_at": datetime.utcnow(),
                "actions": []
            }
            
            # Calculate streak
            today = datetime.utcnow().date()
            last_date = user_doc.get("last_activity_date")
            
            if last_date:
                if isinstance(last_date, datetime):
                    last_date = last_date.date()
                days_diff = (today - last_date).days
                
                if days_diff == 0:
                    # Same day, keep streak
                    pass
                elif days_diff == 1:
                    # Consecutive day, increment streak
                    user_doc["streak_days"] = user_doc.get("streak_days", 0) + 1
                else:
                    # Streak broken
                    user_doc["streak_days"] = 1
            else:
                user_doc["streak_days"] = 1
            
            # Calculate streak bonus
            streak_bonus = min(
                user_doc["streak_days"] * POINTS_CONFIG["streak_bonus_per_day"],
                POINTS_CONFIG["streak_max_bonus"]
            )
            
            total_points_awarded = points + streak_bonus
            
            # Update user document
            user_doc["total_points"] = user_doc.get("total_points", 0) + total_points_awarded
            user_doc["last_activity_date"] = datetime.utcnow()
            user_doc["actions"].append({
                "action": action,
                "points": points,
                "streak_bonus": streak_bonus,
                "song_id": song_id,
                "timestamp": datetime.utcnow()
            })
            
            # Keep only last 100 actions
            if len(user_doc["actions"]) > 100:
                user_doc["actions"] = user_doc["actions"][-100:]
            
            # Save
            self.user_points_collection.update_one(
                {"user_id": user_id},
                {"$set": user_doc},
                upsert=True
            )
            
            logger.info(f"[GAMIFY] {user_id}: +{total_points_awarded} pts ({action} + streak)")
            
            return {
                "success": True,
                "points_awarded": total_points_awarded,
                "base_points": points,
                "streak_bonus": streak_bonus,
                "total_points": user_doc["total_points"],
                "streak_days": user_doc["streak_days"]
            }
            
        except Exception as e:
            logger.error(f"Error awarding points: {e}")
            return {"success": False, "error": str(e)}
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get gamification stats for a user."""
        try:
            self._ensure_gamification_collections()
            
            user_doc = self.user_points_collection.find_one({"user_id": user_id})
            
            if not user_doc:
                return {
                    "user_id": user_id,
                    "total_points": 0,
                    "streak_days": 0,
                    "rank": None,
                    "recent_actions": []
                }
            
            # Get rank
            rank = self.user_points_collection.count_documents({
                "total_points": {"$gt": user_doc.get("total_points", 0)}
            }) + 1
            
            return {
                "user_id": user_id,
                "total_points": user_doc.get("total_points", 0),
                "streak_days": user_doc.get("streak_days", 0),
                "rank": rank,
                "recent_actions": user_doc.get("actions", [])[-10:]  # Last 10
            }
            
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {"user_id": user_id, "total_points": 0, "streak_days": 0, "rank": None}
    
    def get_random_tracks(self, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Get random tracks from the library.
        Used for voting candidates when AzuraCast history isn't sufficient.
        """
        try:
            pipeline = [
                {"$sample": {"size": limit}}
            ]
            
            tracks = list(self.tracks_collection.aggregate(pipeline))
            
            # Clean up ObjectId
            for t in tracks:
                if '_id' in t:
                    t['_id'] = str(t['_id'])
                    
            return tracks
        except Exception as e:
            logger.error(f"Error fetching random tracks: {e}")
            return []
        """
        Get the top users by total points.
        
        Args:
            limit: Number of top users to return
            
        Returns:
            List of user stats sorted by points
        """
        try:
            self._ensure_gamification_collections()
            
            top_users = list(self.user_points_collection.find(
                {},
                {"user_id": 1, "total_points": 1, "streak_days": 1, "_id": 0}
            ).sort("total_points", -1).limit(limit))
            
            # Add rank
            for i, user in enumerate(top_users):
                user["rank"] = i + 1
            
            return top_users
            
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []

    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

    # ========== LIKE / DISLIKE VOTING ==========

    def submit_vote(self, song_id: str, vote: str, user_id: str = "anonymous") -> Dict[str, int]:
        """
        Submit a boolean vote (like/dislike) and return updated counts.
        """
        try:
            if not hasattr(self, 'votes_collection'):
                self.votes_collection = self.db["votes"]
                self.votes_collection.create_index("song_id")
            
            # Store the individual vote
            vote_doc = {
                "song_id": song_id,
                "vote": vote, # 'like' or 'dislike'
                "user_id": user_id,
                "timestamp": datetime.utcnow()
            }
            self.votes_collection.insert_one(vote_doc)
            
            # Count votes for this song
            return self.get_vote_counts(song_id)
            
        except Exception as e:
            logger.error(f"Error submitting vote: {e}")
            return {"likes": 0, "dislikes": 0}

    def get_vote_counts(self, song_id: str) -> Dict[str, int]:
        """Get total likes and dislikes for a song."""
        try:
            if not hasattr(self, 'votes_collection'):
                self.votes_collection = self.db["votes"]

            pipeline = [
                {"$match": {"song_id": song_id}},
                {"$group": {
                    "_id": "$vote", 
                    "count": {"$sum": 1}
                }}
            ]
            results = list(self.votes_collection.aggregate(pipeline))
            
            counts = {"like": 0, "dislike": 0}
            for r in results:
                if r["_id"] in counts:
                    counts[r["_id"]] = r["count"]
            
            return counts
        except Exception as e:
            logger.error(f"Error getting vote counts: {e}")
            return {"like": 0, "dislike": 0}


    # ========== SHOUTOUTS ==========

    def submit_shoutout(self, message: str, sender: str, user_id: str = "anonymous", station_id: int = 1) -> Dict[str, Any]:
        """Submit a shoutout/message."""
        try:
            if not hasattr(self, 'shoutouts_collection'):
                self.shoutouts_collection = self.db["shoutouts"]
                self.shoutouts_collection.create_index([("timestamp", -1)])
            
            doc = {
                "message": message[:280], # Enforce limit
                "sender": sender[:50],
                "user_id": user_id,
                "station_id": station_id,
                "timestamp": datetime.utcnow()
            }
            
            result = self.shoutouts_collection.insert_one(doc)
            
            # Return full doc with string ID
            doc["_id"] = str(result.inserted_id)
            return {"success": True, "shoutout": doc}
            
        except Exception as e:
            logger.error(f"Error submitting shoutout: {e}")
            return {"success": False, "error": str(e)}

    def get_recent_shoutouts(self, limit: int = 20, station_id: int = 1) -> List[Dict[str, Any]]:
        """Get recent shoutouts."""
        try:
            if not hasattr(self, 'shoutouts_collection'):
                return []
                
            cursor = self.shoutouts_collection.find(
                {"station_id": station_id}
            ).sort("timestamp", -1).limit(limit)
            
            results = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                results.append(doc)
            
            return results
        except Exception as e:
            logger.error(f"Error getting shoutouts: {e}")
            return []

if __name__ == "__main__":
    # Test connection
    client = MongoDatabaseClient()
    print("MongoDB client initialized successfully")
    client.close()
