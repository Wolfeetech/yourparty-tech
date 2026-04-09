import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Body
from models.schemas import (
    RatingRequest, MoodRequest, MoodVoteRequest,
    MoodNextVoteRequest, TrackVoteRequest, VoteNextRequest,
    SteeringRequest, ShoutoutRequest
)
from state import state
from tag_writer import write_metadata_to_file
from auth import get_current_active_user, User
from fastapi import Depends

router = APIRouter()
logger = logging.getLogger(__name__)

FEATURE_MOOD_VOTES = os.getenv("FEATURE_MOOD_VOTES", "true").lower() == "true"

def get_metadata_context(song_id: str, station_id: int = 1) -> Optional[Dict[str, Any]]:
    np = state.now_playing.get(station_id, {})
    if np and str(np.get('id')) == str(song_id):
        return {
            "title": np.get("title"),
            "artist": np.get("artist"),
            "album": np.get("album"),
            "cover_art": np.get("art"),
            "genre": np.get("genre")
        }
    return None

from limiter import limiter
from fastapi import Request

@router.post("/rate")
@limiter.limit("10/minute")
async def rate_track(request: Request, rating_request: RatingRequest):
    logger.info(f"Received rating: {rating_request.rating} for song {rating_request.song_id}")
    
    if state.mongo_client:
        result = state.mongo_client.submit_rating(
            song_id=rating_request.song_id,
            rating=rating_request.rating,
            user_id=rating_request.user_id,
            file_path=rating_request.file_path,
            station_id=rating_request.station_id,
            metadata=get_metadata_context(rating_request.song_id, rating_request.station_id)
        )
        if rating_request.file_path and os.path.exists(rating_request.file_path):
            new_stats = result.get("ratings", {})
            avg_rating = new_stats.get("average")
            if avg_rating:
                write_metadata_to_file(rating_request.file_path, rating=avg_rating)     
        return result
    else:
        return {"success": True, "ratings": {"average": float(rating_request.rating), "total": 1, "warning": "Persistence unavailable"}}

@router.get("/ratings")
async def get_ratings(song_id: Optional[str] = None):
    if not state.mongo_client:
        raise HTTPException(status_code=400, detail="MongoDB not connected")
    
    if song_id:
        return state.mongo_client.get_track_rating(song_id=song_id)
    else:
        ratings = state.mongo_client.db.ratings.find({})
        result = {}
        for r in ratings:
            sid = r.get("song_id")
            if sid:
                result[sid] = {
                    "average": r.get("average", 0),
                    "total": r.get("count", 0),
                    "title": r.get("metadata", {}).get("title", "Unknown"),
                    "artist": r.get("metadata", {}).get("artist", "Unknown"),
                    "path": r.get("file_path", "")
                }
        return result

@router.get("/mongo/rating/{song_id}")
async def get_rating_mongo(song_id: str):
    if not state.mongo_client:
        raise HTTPException(status_code=400, detail="MongoDB not connected")
    rating = state.mongo_client.get_track_rating(song_id=song_id)
    return rating if rating else {"average": 0, "total": 0, "distribution": {}}

@router.get("/mongo/tracks/rated")
async def get_rated_tracks(min_rating: float = 0.0):
    if not state.mongo_client:
        raise HTTPException(status_code=400, detail="MongoDB not connected")
    tracks = state.mongo_client.get_all_rated_tracks(min_rating)
    return {"tracks": tracks, "count": len(tracks)}

@router.post("/mood-tag")
async def tag_mood(request: MoodRequest):
    if state.mongo_client:
        return state.mongo_client.submit_mood(
            song_id=request.song_id, mood=request.mood, genre=request.genre, station_id=request.station_id
        )
    return {"success": True, "warning": "Mock Success - DB Missing"}

@router.get("/moods")
async def get_moods(song_id: Optional[str] = None):
    if not state.mongo_client:
         raise HTTPException(status_code=400, detail="MongoDB not connected")
    if song_id:
        return state.mongo_client.get_song_moods(song_id)
    else:
        pipeline = [{"$unwind": "$tags"}, {"$group": {"_id": "$tags", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}]
        agg = state.mongo_client.db.moods.aggregate(pipeline)
        return {"top_moods": [{"tag": r["_id"], "count": r["count"]} for r in agg]}

@router.post("/vote-mood")
@limiter.limit("10/minute")
async def vote_mood(request: Request, mood_request: MoodVoteRequest):
    if not FEATURE_MOOD_VOTES:
        raise HTTPException(status_code=503, detail="Mood voting disabled")
    if not any([mood_request.mood_current, mood_request.mood_next, mood_request.rating, mood_request.vote]):
        raise HTTPException(status_code=400, detail="Vote type required")
    
    result = {"success": True, "song_id": mood_request.song_id, "message": "Vote recorded"}

    if state.mongo_client:
        if mood_request.vote:
            counts = state.mongo_client.submit_vote(mood_request.song_id, mood_request.vote, mood_request.user_id)
            result["vote_counts"] = counts
            if mood_request.vote == "dislike" and counts.get("dislike", 0) >= counts.get("like", 0) + 3:
                 if state.azura_client:
                     await state.azura_client.skip_current_song()
                     result["action_taken"] = "skip"
            if mood_request.vote == "like" and counts.get("like", 0) >= 3:
                 if state.azura_client:
                     try:
                         mid = int(mood_request.song_id) if mood_request.song_id.isdigit() else None
                         if mid:
                             await state.azura_client.add_to_playlist(mid, "Starlight")
                             result["action_taken"] = "playlist_add"
                     except Exception as e:
                         logger.error(f"Playlist add failed: {e}")

        if mood_request.mood_current:
            try:
                state.mongo_client.submit_mood(song_id=mood_request.song_id, mood=mood_request.mood_current, vote_type="community_vote")
                result["mood_current"] = "recorded"
            except Exception as e:
                logger.error(f"Error submitting mood: {e}")
                result["mood_current_error"] = str(e)
            
        if mood_request.mood_next:
            try:
                state.mongo_client.submit_mood_next_vote(song_id=mood_request.song_id, mood=mood_request.mood_next, user_id=mood_request.user_id)
                result["mood_next"] = "recorded"
            except Exception as e:
                 logger.error(f"Error submitting mood_next: {e}")
                 result["mood_next_error"] = str(e)
            
        if mood_request.rating:
            try:
                state.mongo_client.submit_rating(song_id=mood_request.song_id, rating=mood_request.rating, user_id=mood_request.user_id)
            except Exception as e:
                logger.error(f"Error submitting rating: {e}")
                result["rating_error"] = str(e)
            
    # Broadcast 'Pulse' to refresh dashboards
    try:
        from . import realtime
        await realtime.manager.broadcast({"type": "pulse", "target": "moods"})
    except Exception as e:
        logger.error(f"Failed to broadcast pulse: {e}")
            
    return result

@router.post("/shoutout")
@limiter.limit("5/minute")
async def send_shoutout(request: Request, shoutout_request: ShoutoutRequest):
    """Send a shoutout message."""
    if not state.mongo_client:
        return {"success": True, "warning": "Mock Success - DB Missing"}
    
    # 1. Validation
    msg = shoutout_request.message.strip()
    if not msg or len(msg) > 280:
         raise HTTPException(status_code=400, detail="Invalid message length")

    # 2. Persist
    result = state.mongo_client.submit_shoutout(
        message=msg,
        sender=shoutout_request.sender,
        user_id=shoutout_request.user_id,
        station_id=shoutout_request.station_id
    )

    # 3. Broadcast
    if result.get("success"):
        try:
            from . import realtime
            await realtime.manager.broadcast({
                "type": "shoutout", 
                "data": result["shoutout"]
            })
        except Exception as e:
            logger.error(f"Failed to broadcast shoutout: {e}")

    return result

@router.get("/shoutouts")
async def get_shoutouts(station_id: int = 1):
    """Get recent shoutouts."""
    if not state.mongo_client:
        return {"shoutouts": []}
    
    shoutouts = state.mongo_client.get_recent_shoutouts(limit=20, station_id=station_id)
    return {"shoutouts": shoutouts}

@router.post("/vote-next-mood")
@limiter.limit("5/minute")
async def vote_next_mood(request: Request, mood_request: MoodNextVoteRequest):
    if not state.mongo_client:
         raise HTTPException(status_code=400, detail="MongoDB not connected")
    
    state.mongo_client.submit_next_mood_vote(song_id=request.song_id, mood=request.mood_next, user_id="anonymous")
    return {"success": True, "mood_next": request.mood_next, "dominant_next": request.mood_next}

@router.get("/vote-next-candidates")
async def get_vote_candidates():
    import uuid, random
    from datetime import datetime, timedelta
    
    # 1. Check for Active Session
    now = datetime.utcnow()
    station_id = 1 # TODO: Allow passing station_id in query if needed
    current_session = state.voting_session.get(station_id, {})
    candidates = []
    
    is_valid_session = False
    if current_session.get("expires_at") and current_session.get("candidates"):
        try:
            exp = datetime.fromisoformat(current_session["expires_at"])
            if exp > now:
                is_valid_session = True
        except ValueError:
            pass # Invalid format, regenerate
            
    if is_valid_session:
        final_candidates = current_session["candidates"]
        expires_at = current_session["expires_at"]
    else:
        # 2. Generate New Session
        candidates = []
        
        # Intelligent Selection Strategy
        if state.mongo_client:
            # 1. High Rated Track
            rated_tracks = state.mongo_client.get_all_rated_tracks(min_rating=4.0)
            if rated_tracks:
                top_picks = rated_tracks[:50]
                candidates.append(random.choice(top_picks))
                
            # 2. Discovery Track (Untagged)
            untagged = state.mongo_client.get_untagged_tracks(limit=20)
            if untagged:
                candidates.append(random.choice(untagged))
                
            # 3. Wildcard (Random from Library)
            if state.library:
                candidates.append(random.choice(state.library))
            elif state.mongo_client:
                 # Fallback mongo random
                 random_docs = state.mongo_client.get_random_tracks(limit=1)
                 if random_docs:
                     candidates.extend(random_docs)

        # Fallback if strategy yielded nothing
        if not candidates and state.library:
            candidates = random.sample(state.library, min(3, len(state.library)))
        
        # Normalize and Deduplicate
        final_candidates = []
        seen_ids = set()
        
        for c in candidates:
            meta = c.get('metadata', {})
            song_id = str(c.get('song_id') or meta.get('song_id') or uuid.uuid4().hex)
            
            if song_id in seen_ids:
                continue
                
            seen_ids.add(song_id)
            final_candidates.append({
                "id": song_id,
                "title": meta.get('title', 'Unknown Title'),
                "artist": meta.get('artist', 'Unknown Artist'),
                "cover_art": meta.get('art', ''), 
                "media_id": song_id
            })
            
        # Set Expiration (2 minutes from now)
        expiration_time = now + timedelta(minutes=2)
        expires_at = expiration_time.isoformat()
        
        # Update State (ensure key exists)
        if station_id not in state.voting_session:
            state.voting_session[station_id] = {"candidates": [], "expires_at": None}
        state.voting_session[station_id]["candidates"] = final_candidates
        state.voting_session[station_id]["expires_at"] = expires_at
        
    # Get Real Vote Counts (Always Fresh)
    vote_counts = {c['id']: 0 for c in final_candidates}
    if state.mongo_client:
        candidate_ids = [c['id'] for c in final_candidates]
        vote_counts = state.mongo_client.get_next_track_vote_counts(candidate_ids)

    return {
        "candidates": final_candidates, 
        "votes": vote_counts,
        "expires_at": expires_at
    }

@router.post("/vote-next-track")
@limiter.limit("5/minute")
async def vote_for_track(request: Request, track_request: TrackVoteRequest):
    logger.info(f"Track vote: {track_request.track_id} by {track_request.user_id}")
    
    if state.mongo_client:
        success = state.mongo_client.submit_next_track_vote(track_request.track_id, track_request.user_id)
        if success:
             return {"success": True, "message": "Vote recorded"}
        else:
             return {"success": False, "message": "Database error"}
             
    return {"success": True, "message": "Vote recorded (Mock)"}

@router.post("/control/vote-next")
async def vote_next_simple(request: VoteNextRequest):
    """
    Simple vote for next mood (e.g. from bubbles).
    Infers current song_id if possible.
    """
    if not state.mongo_client:
        return {"success": False, "error": "DB unavailable"}
        
    # Infer song_id from now_playing or use generic
    song_id = "global_vote"
    sid = request.station_id
    np = state.now_playing.get(sid, {})
    if np and np.get("id"):
        song_id = str(np.get("id"))
        
    state.mongo_client.submit_next_mood_vote(
        song_id=song_id, 
        mood=request.vote, 
        user_id="anonymous",
        station_id=sid
    )
    return {"success": True, "mood_next": request.vote, "inferred_song": song_id, "station_id": sid}

@router.post("/control/vote-next-winner")
async def calculate_winner(station_id: int = 1):
    """
    Calculate the winner of the current voting session, queue it, and reset.
    """
    import random
    
    # 1. Get Current Candidates
    current_session = state.voting_session.get(station_id, {})
    candidates = current_session.get("candidates", [])
    if not candidates:
        return {"success": False, "message": f"No active voting session for station {station_id}"}
        
    # 2. Count Votes
    winner = None
    if state.mongo_client:
        candidate_ids = [c['id'] for c in candidates]
        counts = state.mongo_client.get_next_track_vote_counts(candidate_ids)
        
        # Find max votes
        max_votes = -1
        leaders = []
        
        for cid, count in counts.items():
            if count > max_votes:
                max_votes = count
                leaders = [cid]
            elif count == max_votes:
                leaders.append(cid)
                
        # Pick winner (random tie-break)
        if leaders:
            winner_id = random.choice(leaders)
            winner = next((c for c in candidates if c['id'] == winner_id), None)
            
    # Fallback if no votes or DB issue: Random Pick
    if not winner:
        winner = random.choice(candidates)
        
    # 3. Queue in AzuraCast
    queued = False
    if state.azura_client and winner:
        # Try numeric ID first if looks like int, else string ID
        mid = winner.get('media_id') or winner.get('id')
        if mid:
            queued = await state.azura_client.queue_track(mid, station_id=station_id)
            
    # 4. Reset Session
    state.voting_session[station_id] = {"candidates": [], "expires_at": None}
    
    return {
        "success": True, 
        "winner": winner, 
        "queued": queued,
        "vote_count": max_votes if 'max_votes' in locals() else 0
    }

@router.get("/control/steer")
async def get_steering(station_id: int = 1):
    return state.steering_status.get(station_id, {"mode": "off", "target": None})

@router.post("/control/steer")
@limiter.limit("20/minute")
async def set_steering(request: Request, steering_request: SteeringRequest, current_user: User = Depends(get_current_active_user)):
    try:
        sid = steering_request.station_id
        if sid not in state.steering_status:
            state.steering_status[sid] = {"mode": "auto", "target": None, "updated_at": None}
            
        state.steering_status[sid]["mode"] = steering_request.mode
        state.steering_status[sid]["target"] = steering_request.target
        from datetime import datetime
        state.steering_status[sid]["updated_at"] = datetime.now().isoformat()
        
        # Broadcast Steering Update
        from routers import realtime
        await realtime.manager.broadcast({
            "type": "steer", 
            "data": state.steering_status[sid]
        }, station_id=str(sid))
        
        return state.steering_status[sid]
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        logger.error(f"STEER ERROR: {error_msg}")
        raise HTTPException(status_code=500, detail=f"Steer Error: {str(e)}\n{error_msg}")

@router.post("/shoutout")
@limiter.limit("5/minute")
async def send_shoutout(request: Request, shoutout: ShoutoutRequest):
    """
    Send a shoutout/message to the studio.
    Stored in MongoDB for the DJ to see.
    """
    if not state.mongo_client:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        # Basic validation
        msg = shoutout.message.strip()
        if not msg or len(msg) > 280:
            raise HTTPException(status_code=400, detail="Invalid message length")

        state.mongo_client.db.shoutouts.insert_one({
            "message": msg,
            "sender": shoutout.sender,
            "user_id": shoutout.user_id,
            "timestamp": datetime.utcnow(),
            "read": False
        })
        return {"status": "sent"}
    except Exception as e:
        logger.error(f"Shoutout error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send shoutout")

@router.get("/shoutouts")
async def get_shoutouts(limit: int = 50, current_user: User = Depends(get_current_active_user)):
    """
    Get recent shoutouts (Admin only).
    """
    if not state.mongo_client:
        return []
    
    cursor = state.mongo_client.db.shoutouts.find().sort("timestamp", -1).limit(limit)
    results = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    
    return results

@router.get("/track-metadata")
async def get_track_metadata(song_id: str = None, title: str = None, artist: str = None):
    """
    Fetch authoritative metadata (Smart Genre, Mood) from Mongo.
    Supports lookup by AzuraCast Song ID (if synced) OR fuzzy Title/Artist match.
    """
    if not state.mongo_client:
        return {"error": "DB Unavailable", "genre": "Unknown", "mood": None}
    
    # Needs at least one identifier
    if not song_id and not (title and artist):
        return {"error": "Missing params", "genre": "Unknown"}

    try:
        track = None
        db = state.mongo_client.db

        # 1. Try AzuraCast Song ID (Direct Match)
        if song_id:
            track = db.tracks.find_one({"song_id": song_id})
            # Fallback: try as Mongo ObjectId
            if not track and len(song_id) == 24:
                try:
                    from bson import ObjectId
                    track = db.tracks.find_one({"_id": ObjectId(song_id)})
                except:
                    pass

        # 2. Try Title + Artist (Case-Insensitive Match)
        if not track and title and artist:
            import re
            t_reg = re.compile(f"^{re.escape(title)}$", re.IGNORECASE)
            a_reg = re.compile(f"^{re.escape(artist)}$", re.IGNORECASE)
            
            track = db.tracks.find_one({
                "metadata.title": t_reg,
                "metadata.artist": a_reg
            })
            
            # Looser fallback: title only
            if not track:
                track = db.tracks.find_one({"metadata.title": t_reg})

        # 3. Return result
        if track:
            return {
                "success": True,
                "genre": track.get("genre", "Unknown"),
                "mood": track.get("mood"),
                "title": track.get("metadata", {}).get("title", track.get("title"))
            }
            
        return {"success": False, "genre": "Unknown", "mood": None}

    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": "Crash", 
            "details": str(e), 
            "trace": traceback.format_exc()
        }
@router.get("/control/queue")
async def get_control_queue(station_id: int = 1):
    """
    Get enriched queue for Control Panel.
    Includes technical metadata (Key/BPM), Moods, and Ratings.
    """
    if not state.azura_client:
        return []

    # 1. Fetch raw queue from AzuraCast
    raw_queue = await state.azura_client.get_station_queue(station_id)
    enriched_queue = []

    for item in raw_queue:
        song = item.get("song", {})
        song_id = song.get("id")
        
        # Base Item
        queue_item = {
            "id": item.get("id"), # Queue Item ID (needed for deletion)
            "cued_at": item.get("cued_at"),
            "is_request": item.get("is_request"),
            "song": {
                "id": song_id,
                "title": song.get("title"),
                "artist": song.get("artist"),
                "art": song.get("art"),
                "custom_fields": song.get("custom_fields", {})
            }
        }

        # Enrichment
        if state.mongo_client and song_id:
            # Moods
            mood_data = state.mongo_client.get_song_moods(str(song_id))
            queue_item["mood_top"] = mood_data.get("top_mood")
            
            # Rating
            rating_data = state.mongo_client.get_track_rating(song_id=str(song_id))
            queue_item["rating"] = rating_data
            
            # Key / BPM / Genre
            meta = state.mongo_client.get_track_metadata(str(song_id))
            queue_item["bpm"] = meta.get("bpm")
            queue_item["initial_key"] = meta.get("initial_key")
            
            # Fallback Genre from Azura if not in Mongo
            if not queue_item.get("genre"):
                queue_item["genre"] = song.get("genre")

        enriched_queue.append(queue_item)

    return enriched_queue

@router.delete("/control/queue/{item_id}")
async def remove_queue_item(item_id: int, station_id: int = 1):
    """Remove an item from the playlist queue."""
    if not state.azura_client:
        raise HTTPException(status_code=503, detail="Backend unavailable")
        
    success = await state.azura_client.delete_queue_item(item_id, station_id)
    if success:
        return {"success": True}
    else:
        raise HTTPException(status_code=500, detail="Failed to remove item")

@router.get("/control/library/search")
async def search_library_handler(q: str, station_id: int = 1):
    """Search for tracks in the library (via AzuraCast Requests API)."""
    if not state.azura_client: 
        return []
    return await state.azura_client.search_requests(q, station_id)

@router.post("/control/queue")
async def add_to_queue_handler(payload: dict):
    """Add a track to the queue via Request API."""
    if not state.azura_client: 
        raise HTTPException(status_code=503, detail="Backend unavailable")
    
    mid = payload.get("media_id") or payload.get("song_id") # Accept either
    sid = payload.get("station_id", 1)
    
    if not mid: 
        raise HTTPException(status_code=400, detail="media_id required")
    
    success = await state.azura_client.queue_track(mid, sid)
    return {"success": success}


# =============================================
# CURATOR PLAYLIST MANAGEMENT (NTS-Lite)
# =============================================

@router.get("/curator/schedule")
async def get_curator_schedule(station_id: int = 1):
    """Get aggregated schedule for all playlists."""
    if not state.azura_client:
        return {"schedule": []}
    
    playlists = await state.azura_client.get_playlists(station_id)
    schedule_items = []
    
    for pl in playlists:
        # We need to fetch schedule for each, or rely on a bulk fetch if available?
        # AzuraCast doesn't typically send schedule in list summary.
        # But iterating all might be slow.
        # For now, let's fetch schedule for active playlists only or all.
        sched = await state.azura_client.get_playlist_schedule(pl["id"], station_id)
        if sched:
            for s in sched:
                schedule_items.append({
                    **s,
                    "playlist_name": pl["name"],
                    "playlist_id": pl["id"],
                    "colour": pl.get("type", "default") # Use type/weight as color proxy
                })
                
    return {"schedule": schedule_items}


@router.get("/curator/playlists")
async def get_curator_playlists(station_id: int = 1):
    """Get all playlists for the curator dashboard (Decoupled/Cached)."""
    
    # 1. Try Fast Read (MongoDB)
    if state.mongo_client:
        cached = state.mongo_client.get_cached_playlists()
        if cached:
             return cached
             
    # 2. Fallback: Slow Read (Direct) + Trigger Sync
    if not state.azura_client:
        raise HTTPException(status_code=503, detail="Backend unavailable")
    
    logger.warning("Cache miss for playlists. Fetching direct from AzuraCast...")
    playlists = await state.azura_client.get_playlists(station_id)
    
    # Enrich with schedule info (Slow part)
    enriched = []
    for pl in playlists:
        schedule = await state.azura_client.get_playlist_schedule(pl["id"], station_id)
        enriched.append({
            "id": pl.get("id"),
            "name": pl.get("name"),
            "is_enabled": pl.get("is_enabled"),
            "weight": pl.get("weight"),
            "type": pl.get("type"),
            "num_songs": pl.get("num_songs", 0),
            "total_length": pl.get("total_length", 0),
            "schedule": schedule
        })

    # Saving to cache for next time
    if state.mongo_client:
        state.mongo_client.save_playlists(enriched)
    
    return enriched


@router.post("/curator/playlists")
async def create_curator_playlist(payload: Dict = Body(...), station_id: int = 1):
    """Create a new playlist."""
    if not state.azura_client:
        raise HTTPException(status_code=503, detail="Backend unavailable")
    
    name = payload.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Playlist name required")
    
    result = await state.azura_client.create_playlist(
        name=name,
        weight=payload.get("weight", 3),
        station_id=station_id
    )
    
    if result:
        return {"success": True, "playlist": result}
    else:
        raise HTTPException(status_code=500, detail="Failed to create playlist")


@router.get("/curator/playlists/{playlist_id}")
async def get_curator_playlist(playlist_id: int, station_id: int = 1):
    """Get single playlist with tracks."""
    if not state.azura_client:
        raise HTTPException(status_code=503, detail="Backend unavailable")
    
    playlist = await state.azura_client.get_playlist(playlist_id, station_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    # Get tracks in this playlist
    tracks = await state.azura_client.get_playlist_media(playlist_id, station_id)
    
    # Get schedule
    schedule = await state.azura_client.get_playlist_schedule(playlist_id, station_id)
    
    return {
        **playlist,
        "tracks": tracks,
        "schedule": schedule
    }


@router.put("/curator/playlists/{playlist_id}")
async def update_curator_playlist(playlist_id: int, payload: Dict = Body(...), station_id: int = 1):
    """Update playlist settings."""
    if not state.azura_client:
        raise HTTPException(status_code=503, detail="Backend unavailable")
    
    result = await state.azura_client.update_playlist(playlist_id, payload, station_id)
    return {"success": True, "playlist": result}


@router.delete("/curator/playlists/{playlist_id}")
async def delete_curator_playlist(playlist_id: int, station_id: int = 1):
    """Delete a playlist."""
    if not state.azura_client:
        raise HTTPException(status_code=503, detail="Backend unavailable")
    
    success = await state.azura_client.delete_playlist(playlist_id, station_id)
    if success:
        return {"success": True}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete playlist")


@router.post("/curator/playlists/{playlist_id}/tracks")
async def add_track_to_playlist(playlist_id: int, payload: Dict = Body(...), station_id: int = 1):
    """Add a track to a playlist."""
    if not state.azura_client:
        raise HTTPException(status_code=503, detail="Backend unavailable")
    
    media_id = payload.get("media_id")
    if not media_id:
        raise HTTPException(status_code=400, detail="media_id required")
    
    # Get playlist name for logging
    playlist = await state.azura_client.get_playlist(playlist_id, station_id)
    playlist_name = playlist.get("name", "") if playlist else ""
    
    success = await state.azura_client.add_media_to_playlist(
        media_id=media_id,
        playlist_id=playlist_id,
        playlist_name=playlist_name,
        station_id=station_id
    )
    
    return {"success": success}


@router.post("/curator/playlists/{playlist_id}/schedule")
async def schedule_playlist(playlist_id: int, payload: Dict = Body(...), station_id: int = 1):
    """Schedule a playlist for specific time slots.
    
    Body: {
        "start_time": "20:00",
        "end_time": "22:00", 
        "days": [4, 5]  // 0=Mon, 6=Sun
    }
    """
    if not state.azura_client:
        raise HTTPException(status_code=503, detail="Backend unavailable")
    
    start_time = payload.get("start_time")
    end_time = payload.get("end_time")
    days = payload.get("days", [])
    
    if not start_time or not end_time:
        raise HTTPException(status_code=400, detail="start_time and end_time required")
    
    result = await state.azura_client.add_playlist_schedule(
        playlist_id=playlist_id,
        start_time=start_time,
        end_time=end_time,
        days=days,
        station_id=station_id
    )
    
    return {"success": True, "schedule": result}


@router.delete("/curator/playlists/{playlist_id}/schedule/{schedule_id}")
async def delete_playlist_schedule(playlist_id: int, schedule_id: int, station_id: int = 1):
    """Remove a schedule from a playlist."""
    if not state.azura_client:
        raise HTTPException(status_code=503, detail="Backend unavailable")
    
    success = await state.azura_client.delete_playlist_schedule(playlist_id, schedule_id, station_id)
    if success:
        return {"success": True}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete schedule")


@router.get("/curator/schedule")
async def get_curator_schedule(station_id: int = 1):
    """Get full station schedule with all scheduled playlists."""
    if not state.azura_client:
        raise HTTPException(status_code=503, detail="Backend unavailable")
    
    playlists = await state.azura_client.get_playlists(station_id)
    
    schedule_items = []
    for pl in playlists:
        if not pl.get("is_enabled"):
            continue
        schedule = await state.azura_client.get_playlist_schedule(pl["id"], station_id)
        for s in schedule:
            schedule_items.append({
                "playlist_id": pl["id"],
                "playlist_name": pl["name"],
                "start_time": s.get("start_time"),
                "end_time": s.get("end_time"),
                "days": s.get("days", []),
                "schedule_id": s.get("id")
            })
    
    # Sort by start time
    schedule_items.sort(key=lambda x: x.get("start_time", ""))
    
    return {"schedule": schedule_items}
