import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException
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
    if not any([request.mood_current, request.mood_next, request.rating, request.vote]):
        raise HTTPException(status_code=400, detail="Vote type required")
    
    result = {"success": True, "song_id": request.song_id, "message": "Vote recorded"}

    if state.mongo_client:
        if request.vote:
            counts = state.mongo_client.submit_vote(request.song_id, request.vote, request.user_id)
            result["vote_counts"] = counts
            if request.vote == "dislike" and counts.get("dislike", 0) >= counts.get("like", 0) + 3:
                 if state.azura_client:
                     await state.azura_client.skip_current_song()
                     result["action_taken"] = "skip"
            if request.vote == "like" and counts.get("like", 0) >= 3:
                 if state.azura_client:
                     try:
                         mid = int(request.song_id) if request.song_id.isdigit() else None
                         if mid:
                             await state.azura_client.add_to_playlist(mid, "Starlight")
                             result["action_taken"] = "playlist_add"
                     except Exception as e:
                         logger.error(f"Playlist add failed: {e}")

        if request.mood_current:
            state.mongo_client.submit_mood(song_id=request.song_id, mood=request.mood_current, vote_type="community_vote")
            result["mood_current"] = "recorded"
            
        if request.mood_next:
            state.mongo_client.submit_next_mood_vote(song_id=request.song_id, mood=request.mood_next, user_id=request.user_id)
            result["mood_next"] = "recorded"
            
        if request.rating:
            state.mongo_client.submit_rating(song_id=request.song_id, rating=request.rating, user_id=request.user_id)
            
    return result

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
    sid = steering_request.station_id
    if sid not in state.steering_status:
        state.steering_status[sid] = {"mode": "auto", "target": None, "updated_at": None}
        
    state.steering_status[sid]["mode"] = steering_request.mode
    state.steering_status[sid]["target"] = steering_request.target
    from datetime import datetime
    state.steering_status[sid]["updated_at"] = datetime.now().isoformat()
    return state.steering_status[sid]

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
