import logging
from typing import Dict, Any, Optional, List
from pymongo import MongoClient
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDatabaseClient:
    """
    Client for MongoDB integration - handles ratings, metadata, and sync with library.
    """
    def __init__(self, connection_string: str = "mongodb://localhost:27017/", database_name: str = "radio_ratings"):
        """
        Initialize MongoDB client.
        
        Args:
            connection_string: MongoDB connection string (default: localhost)
            database_name: Database name for ratings storage
        """
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client[database_name]
            self.ratings_collection = self.db["ratings"]
            self.tracks_collection = self.db["tracks"]
            self.sync_log_collection = self.db["sync_log"]
            
            # Create indexes for performance
            self.ratings_collection.create_index("song_id")
            self.ratings_collection.create_index("user_id")
            self.tracks_collection.create_index("file_path", unique=True)
            self.tracks_collection.create_index("song_id")
            
            logger.info(f"Connected to MongoDB: {database_name}")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise

    def get_track_rating(self, file_path: str = None, song_id: str = None) -> Optional[Dict[str, Any]]:
        """
        Get aggregated rating for a track.
        
        Args:
            file_path: Local file path
            song_id: AzuraCast song ID
        
        Returns:
            Dict with rating statistics or None
        """
        try:
            query = {}
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
                     file_path: str = None) -> Dict[str, Any]:
        """
        Submit a new rating for a track.
        
        Args:
            song_id: AzuraCast song ID
            rating: Rating value (1-5)
            user_id: User identifier
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
                "timestamp": datetime.utcnow(),
                "file_path": file_path
            }
            
            # Insert rating
            self.ratings_collection.insert_one(rating_doc)
            
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

    def submit_mood(self, song_id: str, mood: str = None, genre: str = None, user_id: str = "anonymous") -> Dict[str, Any]:
        """
        Submit a new mood or genre tag for a track.
        """
        try:
            doc = {
                "song_id": song_id,
                "user_id": user_id,
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
            logger.error(f"Error getting moods: {e}")
            return {}

    def get_song_moods(self, song_id: str) -> Dict[str, Any]:
        """Get mood tags for a specific song."""
        try:
            if not hasattr(self, 'moods_collection'):
                 self.moods_collection = self.db["moods"]
            
            # Get most popular mood for this song
            pipeline = [
                {"$match": {"song_id": song_id}},
                {"$group": {"_id": "$mood", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 1}
            ]
            
            top_mood = None
            results = list(self.moods_collection.aggregate(pipeline))
            if results and results[0]["_id"]:
                top_mood = results[0]["_id"]
                
            return {
                "top_mood": top_mood,
                "all_moods": [r["_id"] for r in results] # Ideally return all, but pipeline limited to 1.
            }
        except Exception as e:
            logger.error(f"Error getting song moods: {e}")
            return {"top_mood": None}


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

    def get_all_rated_tracks(self, min_rating: float = 0.0) -> List[Dict[str, Any]]:
        """
        Get all tracks with ratings above a threshold.
        
        Args:
            min_rating: Minimum average rating filter
        
        Returns:
            List of tracks with their ratings
        """
        try:
            # Aggregate tracks with ratings
            pipeline = [
                {"$group": {
                    "_id": "$song_id",
                    "average": {"$avg": "$rating"},
                    "total": {"$sum": 1}
                }},
                {"$match": {"average": {"$gte": min_rating}}},
                {"$sort": {"average": -1}}
            ]
            
            raw_results = list(self.ratings_collection.aggregate(pipeline))
            logger.info(f"DEBUG: Raw Aggregation Found {len(raw_results)} groups.")
            for r in raw_results:
                 logger.info(f"DEBUG Group: {r}")
            
            # Enrich with track metadata
            result = []
            for rating in raw_results:
                if not rating["_id"]:
                    continue # Skip null grouping (old data?))
                track = self.tracks_collection.find_one({"song_id": rating["_id"]})
                if track:
                    result.append({
                        "song_id": rating["_id"],
                        "file_path": track.get("file_path"),
                        "metadata": track.get("metadata", {}),
                        "rating": {
                            "average": round(rating["average"], 2),
                            "total": rating["total"]
                        }
                    })
                else:
                    # Include even if track is missing, so sync script can try to heal it
                    result.append({
                        "song_id": rating["_id"],
                        "file_path": None,
                        "metadata": {},
                        "rating": {
                            "average": round(rating["average"], 2),
                            "total": rating["total"]
                        }
                    })

                # Post-processing: Fallback for Unknown Title/Artist
                last_entry = result[-1]
                meta = last_entry["metadata"]
                if not meta.get("title") or not meta.get("artist"):
                    fp = last_entry.get("file_path")
                    if fp:
                        import os
                        filename = os.path.basename(fp)
                        name_part = os.path.splitext(filename)[0]
                        if " - " in name_part:
                            parts = name_part.split(" - ", 1)
                            if not meta.get("artist"): meta["artist"] = parts[0]
                            if not meta.get("title"): meta["title"] = parts[1]
                        else:
                            if not meta.get("title"): meta["title"] = name_part
                            if not meta.get("artist"): meta["artist"] = "Unknown Artist"
                        last_entry["metadata"] = meta
            
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

    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


if __name__ == "__main__":
    # Test connection
    client = MongoDatabaseClient()
    print("MongoDB client initialized successfully")
    client.close()
