"""
Redis Vote State Manager
YourParty.tech V2 - Real-time Voting Engine

Handles real-time vote aggregation using Redis:
- Vote counting with automatic expiry
- Next-mood consensus calculation
- Track queue prioritization
- WebSocket broadcast coordination
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum

logger = logging.getLogger("redis-votes")

# Feature flag - allows gradual rollout
FEATURE_V2_REDIS = os.getenv("FEATURE_V2_REDIS", "false").lower() == "true"


class VoteType(Enum):
    MOOD_CURRENT = "mood_current"  # Tag for current song
    MOOD_NEXT = "mood_next"        # Vote for what plays next
    TRACK_NEXT = "track_next"      # Vote for specific track
    RATING = "rating"              # 1-5 star rating


class RedisVoteManager:
    """
    Manages real-time voting state using Redis.
    
    Key structure:
    - votes:{station_id}:mood_current:{song_id} -> Hash {mood: count}
    - votes:{station_id}:mood_next -> Hash {mood: count}
    - votes:{station_id}:track_next -> Hash {song_id: count}
    - votes:{station_id}:ratings:{song_id} -> List of ratings
    - user:{station_id}:{user_id}:cooldown:{vote_type} -> TTL key
    """
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.client = None
        self.enabled = FEATURE_V2_REDIS
        
        if self.enabled:
            self._connect()
    
    def _connect(self):
        """Lazy connection to Redis"""
        try:
            import redis
            self.client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            # Test connection
            self.client.ping()
            logger.info(f"Redis connected: {self.redis_url.split('@')[-1]}")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            self.client = None
            self.enabled = False
    
    def _key(self, *parts) -> str:
        """Build Redis key from parts"""
        return ":".join(str(p) for p in parts)
    
    # ========================================
    # VOTE SUBMISSION
    # ========================================
    
    async def submit_mood_current(
        self,
        song_id: str,
        mood: str,
        user_id: str = "anonymous",
        station_id: int = 1
    ) -> Dict[str, Any]:
        """
        Record a mood tag for the current song.
        Returns updated vote counts.
        """
        if not self.enabled or not self.client:
            return {"status": "disabled", "fallback": True}
        
        # Check cooldown (1 vote per song per user)
        cooldown_key = self._key("user", station_id, user_id, "cooldown", "mood", song_id)
        if self.client.exists(cooldown_key):
            return {"status": "cooldown", "message": "Already voted for this song"}
        
        # Increment mood count
        vote_key = self._key("votes", station_id, "mood_current", song_id)
        self.client.hincrby(vote_key, mood, 1)
        
        # Set expiry (votes expire after 24 hours)
        self.client.expire(vote_key, 86400)
        
        # Set user cooldown (5 minutes per song)
        self.client.setex(cooldown_key, 300, "1")
        
        # Get updated counts
        counts = self.client.hgetall(vote_key)
        
        return {
            "status": "success",
            "song_id": song_id,
            "mood": mood,
            "counts": {k: int(v) for k, v in counts.items()},
            "top_mood": self._get_top_mood(counts)
        }
    
    async def submit_mood_next(
        self,
        mood: str,
        user_id: str = "anonymous",
        station_id: int = 1
    ) -> Dict[str, Any]:
        """
        Vote for the mood of the next track.
        Votes expire after the voting window (e.g., 5 minutes).
        """
        if not self.enabled or not self.client:
            return {"status": "disabled", "fallback": True}
        
        # Check cooldown
        cooldown_key = self._key("user", station_id, user_id, "cooldown", "mood_next")
        if self.client.exists(cooldown_key):
            return {"status": "cooldown", "message": "Vote cooldown active"}
        
        # Increment vote
        vote_key = self._key("votes", station_id, "mood_next")
        self.client.hincrby(vote_key, mood, 1)
        
        # Set cooldown (2 minutes between mood_next votes)
        self.client.setex(cooldown_key, 120, "1")
        
        # Get counts
        counts = self.client.hgetall(vote_key)
        
        return {
            "status": "success",
            "mood": mood,
            "counts": {k: int(v) for k, v in counts.items()},
            "leading": self._get_top_mood(counts)
        }
    
    async def submit_track_vote(
        self,
        song_id: str,
        user_id: str = "anonymous",
        station_id: int = 1
    ) -> Dict[str, Any]:
        """
        Vote for a specific track to play next.
        """
        if not self.enabled or not self.client:
            return {"status": "disabled", "fallback": True}
        
        # Check cooldown
        cooldown_key = self._key("user", station_id, user_id, "cooldown", "track_next")
        if self.client.exists(cooldown_key):
            return {"status": "cooldown"}
        
        # Increment
        vote_key = self._key("votes", station_id, "track_next")
        self.client.hincrby(vote_key, song_id, 1)
        
        # Cooldown
        self.client.setex(cooldown_key, 180, "1")  # 3 minutes
        
        counts = self.client.hgetall(vote_key)
        
        return {
            "status": "success",
            "song_id": song_id,
            "counts": {k: int(v) for k, v in counts.items()},
            "leading": max(counts, key=lambda k: int(counts[k])) if counts else None
        }
    
    async def submit_rating(
        self,
        song_id: str,
        rating: int,
        user_id: str = "anonymous",
        station_id: int = 1
    ) -> Dict[str, Any]:
        """
        Submit a 1-5 star rating for a song.
        """
        if not self.enabled or not self.client:
            return {"status": "disabled", "fallback": True}
        
        if rating < 1 or rating > 5:
            return {"status": "error", "message": "Rating must be 1-5"}
        
        # Store in sorted set for average calculation
        key = self._key("votes", station_id, "ratings", song_id)
        
        # Add timestamped rating
        timestamp = int(datetime.now().timestamp())
        self.client.zadd(key, {f"{user_id}:{timestamp}": rating})
        
        # Calculate average
        all_ratings = self.client.zrange(key, 0, -1, withscores=True)
        avg = sum(r[1] for r in all_ratings) / len(all_ratings) if all_ratings else 0
        
        return {
            "status": "success",
            "song_id": song_id,
            "rating": rating,
            "average": round(avg, 2),
            "total": len(all_ratings)
        }
    
    # ========================================
    # VOTE RETRIEVAL
    # ========================================
    
    def get_mood_consensus(self, station_id: int = 1) -> Optional[str]:
        """Get the winning mood for next track selection"""
        if not self.enabled or not self.client:
            return None
        
        vote_key = self._key("votes", station_id, "mood_next")
        counts = self.client.hgetall(vote_key)
        
        if not counts:
            return None
        
        return max(counts, key=lambda k: int(counts[k]))
    
    def get_winning_track(self, station_id: int = 1) -> Optional[str]:
        """Get the track with most votes"""
        if not self.enabled or not self.client:
            return None
        
        vote_key = self._key("votes", station_id, "track_next")
        counts = self.client.hgetall(vote_key)
        
        if not counts:
            return None
        
        return max(counts, key=lambda k: int(counts[k]))
    
    def get_song_moods(self, song_id: str, station_id: int = 1) -> Dict[str, int]:
        """Get mood vote counts for a song"""
        if not self.enabled or not self.client:
            return {}
        
        vote_key = self._key("votes", station_id, "mood_current", song_id)
        counts = self.client.hgetall(vote_key)
        
        return {k: int(v) for k, v in counts.items()}
    
    def get_song_rating(self, song_id: str, station_id: int = 1) -> Dict[str, Any]:
        """Get rating stats for a song"""
        if not self.enabled or not self.client:
            return {"average": 0, "total": 0}
        
        key = self._key("votes", station_id, "ratings", song_id)
        all_ratings = self.client.zrange(key, 0, -1, withscores=True)
        
        if not all_ratings:
            return {"average": 0, "total": 0}
        
        avg = sum(r[1] for r in all_ratings) / len(all_ratings)
        return {
            "average": round(avg, 2),
            "total": len(all_ratings)
        }
    
    # ========================================
    # VOTE WINDOW MANAGEMENT
    # ========================================
    
    def reset_next_votes(self, station_id: int = 1):
        """Clear next-track/mood votes after selection"""
        if not self.enabled or not self.client:
            return
        
        self.client.delete(
            self._key("votes", station_id, "mood_next"),
            self._key("votes", station_id, "track_next")
        )
        logger.info(f"Reset next-track votes for station {station_id}")
    
    def get_vote_summary(self, station_id: int = 1) -> Dict[str, Any]:
        """Get full voting state summary for debugging/dashboard"""
        if not self.enabled or not self.client:
            return {"enabled": False}
        
        mood_next = self.client.hgetall(self._key("votes", station_id, "mood_next"))
        track_next = self.client.hgetall(self._key("votes", station_id, "track_next"))
        
        return {
            "enabled": True,
            "station_id": station_id,
            "mood_next_votes": {k: int(v) for k, v in mood_next.items()},
            "track_next_votes": {k: int(v) for k, v in track_next.items()},
            "leading_mood": self._get_top_mood(mood_next),
            "leading_track": max(track_next, key=lambda k: int(track_next[k])) if track_next else None
        }
    
    # ========================================
    # HELPERS
    # ========================================
    
    def _get_top_mood(self, counts: Dict[str, str]) -> Optional[str]:
        """Get mood with highest count"""
        if not counts:
            return None
        return max(counts, key=lambda k: int(counts[k]))
    
    def is_enabled(self) -> bool:
        """Check if Redis voting is active"""
        return self.enabled and self.client is not None


# Singleton instance
_vote_manager: Optional[RedisVoteManager] = None


def get_vote_manager() -> RedisVoteManager:
    """Get or create singleton vote manager"""
    global _vote_manager
    if _vote_manager is None:
        _vote_manager = RedisVoteManager()
    return _vote_manager
