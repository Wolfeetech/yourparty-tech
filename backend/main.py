from __future__ import annotations

import json
import os
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict
from datetime import timedelta

import httpx
from fastapi import BackgroundTasks, FastAPI, Request, Depends, HTTPException, status
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.security import OAuth2PasswordRequestForm
from mutagen.id3 import ID3, TXXX

from auth import Token, User, create_access_token, get_current_active_user, users_db, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES

from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(
    title="YourParty Radio API",
    description="Backend for Radio Steering and Metadata",
    version="1.0.0"
)

# Enable Prometheus Metrics
Instrumentator().instrument(app).expose(app)

# Load Allowed Origins from Env
raw_origins = os.getenv("ALLOWED_ORIGINS", '["*"]')
try:
    origins_list = json.loads(raw_origins)
except json.JSONDecodeError:
    origins_list = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)


# ---------------------------------------------------------------------------
# Rating persistence
# ---------------------------------------------------------------------------

from pymongo import MongoClient, ReturnDocument

# ---------------------------------------------------------------------------
# MongoDB Configuration & Persistence
# ---------------------------------------------------------------------------

MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME", "root")
MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "4f5cd00532af49b5941d6f6385b2e0bf")
MONGO_HOST = os.getenv("MONGO_HOST", "mongo")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")

MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}"

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client["yourparty"]
ratings_col = db["ratings"]
moods_col = db["moods"]
steering_col = db["steering"]
steering_votes_col = db["steering_votes"]

def get_steering_state():
    # Check if we have an active "forced" override (Admin)
    state = steering_col.find_one({"_id": "current"})
    
    # Handle missing state doc
    if not state:
        state = {"state": {"mode": "auto"}}

    # Check community votes if mode is auto or community
    # Logic: If Admin Mode is 'auto', we look at community votes from last 10 mins
    admin_mode = state.get("state", {}).get("mode", "auto")
    admin_target = state.get("state", {}).get("target")

    if admin_mode != "auto":
        return {"mode": admin_mode, "target": admin_target, "source": "admin"}
        
    # Community Logic
    # Get votes from last 10 minutes
    cutoff = int(time.time()) - 600
    pipeline = [
        {"$match": {"timestamp": {"$gt": cutoff}}},
        {"$group": {"_id": "$vote", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 1}
    ]
    
    votes = list(steering_votes_col.aggregate(pipeline))
    if votes:
        winner = votes[0]["_id"]
        return {"mode": "mood", "target": winner, "source": "community"}
        
    return {"mode": "auto", "target": None, "source": "random"}

def set_steering_state(mode: str, target: str = None):
    steering_col.update_one(
        {"_id": "current"},
        {"$set": {"state": {"mode": mode, "target": target}, "updated_at": int(time.time())}},
        upsert=True
    )

def get_rating_counts(song_id: str) -> Dict[str, Any]:
    entry = ratings_col.find_one({"_id": song_id})
    if not entry:
        return {
            "like": 0,
            "dislike": 0,
            "neutral": 0,
            "distribution": {str(k): 0 for k in range(1, 6)},
            "total": 0,
            "average": 0.0,
            "updated_at": 0,
        }
    
    dist = entry.get("distribution", {})
    # Ensure keys are strings for JSON response
    normalized_dist = {str(k): dist.get(str(k), 0) for k in range(1, 6)}
    
    return {
        "like": entry.get("like", 0),
        "dislike": entry.get("dislike", 0),
        "neutral": entry.get("neutral", 0),
        "distribution": normalized_dist,
        "total": entry.get("total", 0),
        "average": entry.get("average", 0.0),
        "updated_at": entry.get("updated_at", 0),
    }

def update_rating_in_db(song_id: str, vote: str = None, rating_value: int = None):
    update_ops = {
        "$set": {"updated_at": int(time.time())},
        "$inc": {"total": 0} # Placeholder to ensure $inc exists
    }
    
    inc = {}
    if vote:
        inc[vote] = 1
    
    if rating_value:
        inc[f"distribution.{rating_value}"] = 1
        inc["total"] = 1
        
    if inc:
        update_ops["$inc"] = inc
    else:
        del update_ops["$inc"]

    # Upsert the document
    entry = ratings_col.find_one_and_update(
        {"_id": song_id},
        update_ops,
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    
    # Recalculate average (MongoDB aggregation or simple math in python)
    # Simple math here since we have the doc
    dist = entry.get("distribution", {})
    total_stars = sum(dist.get(str(k), 0) for k in range(1, 6))
    weighted_sum = sum(k * dist.get(str(k), 0) for k in range(1, 6))
    
    new_avg = round(weighted_sum / total_stars, 3) if total_stars > 0 else 0.0
    
    ratings_col.update_one({"_id": song_id}, {"$set": {"average": new_avg}})
    
    return get_rating_counts(song_id)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

AZURACAST_URL = os.getenv("AZURACAST_URL", "http://192.168.178.210")
AZURACAST_API_KEY = os.getenv("AZURACAST_API_KEY")
MUSIC_DIR = Path(os.getenv("MUSIC_DIR", "/var/radio/music"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    if not AZURACAST_URL or not AZURACAST_API_KEY:
        print("[WARN] AZURACAST_URL or AZURACAST_API_KEY missing  API will not function correctly.")
    yield
    # shutdown (no-op)


# attach lifespan to the app
app.router.lifespan_context = lifespan


# ---------------------------------------------------------------------------
# REST endpoints
# ---------------------------------------------------------------------------


@app.get("/")
def read_root() -> Dict[str, str]:
    return {"status": "ok", "message": "Welcome to RadioStudio API"}


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get("/status")
async def get_enriched_status():
    url = f"{AZURACAST_URL}/api/nowplaying/1"
    headers = {"Authorization": f"Bearer {AZURACAST_API_KEY}"}

    try:
        async with httpx.AsyncClient(timeout=60, follow_redirects=True, verify=False) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as exc:
        return JSONResponse(
            status_code=exc.response.status_code,
            content={"error": f"AzuraCast HTTP {exc.response.status_code}", "details": exc.response.text},
        )
    except httpx.RequestError as exc:
        return JSONResponse(status_code=502, content={"error": f"AzuraCast unreachable: {exc}"})

    if isinstance(data, dict):
        now_playing = data.get("now_playing") or {}
        song = now_playing.get("song") or {}
        song_id = song.get("id")
        if song_id:
            # Add rating data
            song["rating"] = get_rating_counts(song_id)
            # Add mood data
            mood_doc = moods_col.find_one({"_id": song_id}) or {}
            song["moods"] = mood_doc.get("moods", {})
            song["top_mood"] = mood_doc.get("top_mood")
            song["genres"] = mood_doc.get("genres", {})
            song["top_genre"] = mood_doc.get("top_genre")
            data["now_playing"]["song"] = song

    return data


@app.get("/history")
async def get_history():
    url = f"{AZURACAST_URL}/api/station/1/history"
    headers = {"Authorization": f"Bearer {AZURACAST_API_KEY}"}

    try:
        async with httpx.AsyncClient(timeout=60, follow_redirects=True, verify=False) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as exc:
        return JSONResponse(
            status_code=exc.response.status_code,
            content={"error": f"AzuraCast HTTP {exc.response.status_code}", "details": exc.response.text},
        )
    except httpx.RequestError as exc:
        return JSONResponse(status_code=502, content={"error": f"AzuraCast unreachable: {exc}"})

    if isinstance(data, list):
        for entry in data:
            song = entry.get("song") if isinstance(entry, dict) else None
            song_id = song.get("id") if isinstance(song, dict) else None
            if song_id:
                # Add rating data
                song["rating"] = get_rating_counts(song_id)
                # Add mood data
                mood_doc = moods_col.find_one({"_id": song_id}) or {}
                song["moods"] = mood_doc.get("moods", {})
                song["top_mood"] = mood_doc.get("top_mood")
                song["genres"] = mood_doc.get("genres", {})
                song["top_genre"] = mood_doc.get("top_genre")

    return data


@app.get("/library")
async def get_library():
    # AzuraCast API: /api/station/{station_id}/files
    url = f"{AZURACAST_URL}/api/station/1/files"
    headers = {"Authorization": f"Bearer {AZURACAST_API_KEY}"}

    try:
        async with httpx.AsyncClient(timeout=60, follow_redirects=True, verify=False) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as exc:
        return JSONResponse(
            status_code=exc.response.status_code,
            content={"error": f"AzuraCast HTTP {exc.response.status_code}", "details": exc.response.text},
        )
    except httpx.RequestError as exc:
        return JSONResponse(status_code=502, content={"error": f"AzuraCast unreachable: {exc}"})

    return data


@app.post("/rate")
async def rate_track(request: Request, background_tasks: BackgroundTasks):
    forwarded = request.headers.get("X-Forwarded-For")
    ip = forwarded.split(",")[0] if forwarded else request.client.host
    
    # Check rate limit (10 votes per 10 minutes per IP)
    cutoff = int(time.time()) - 600
    recent_votes = db["vote_logs"].count_documents({
        "ip": ip,
        "updated_at": {"$gt": cutoff}
    })
    
    if recent_votes > 10:
        return JSONResponse(status_code=429, content={"error": "Rate limit exceeded. Try again later."})

    try:
        payload = await request.json()
    except json.JSONDecodeError:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON payload."})

    song_id = str(payload.get("song_id", "")).strip()
    if not song_id:
        return JSONResponse(status_code=400, content={"error": "'song_id' is required."})

    vote = payload.get("vote")
    if isinstance(vote, str):
        vote = vote.lower().strip()
        if vote == "up":
            vote = "like"
        elif vote == "down":
            vote = "dislike"
    else:
        vote = None

    rating_value = payload.get("rating")
    try:
        rating_value = int(rating_value) if rating_value is not None else None
    except (TypeError, ValueError):
        rating_value = None

    if vote and vote not in {"like", "dislike", "neutral"}:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid vote. Must be one of 'like', 'dislike', 'neutral'."},
        )

    if vote is None and rating_value is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Provide at least one of 'vote' or numeric 'rating'."},
        )

    # --- METADATA SYNC (Robustness Fix) ---
    # If the frontend sends title/artist, update our metadata store (moods_col)
    title = str(payload.get("title", "")).strip()
    artist = str(payload.get("artist", "")).strip()
    
    if title or artist:
        update_meta = { "$set": { "updated_at": int(time.time()) } }
        if title: update_meta["$set"]["title"] = title
        if artist: update_meta["$set"]["artist"] = artist
        
        # Upsert into moods collection (which serves as our master metadata list)
        moods_col.update_one({"_id": song_id}, update_meta, upsert=True)

    # Update DB
    new_counts = update_rating_in_db(song_id, vote, rating_value)
    
    # Log vote for rate limiting
    db["vote_logs"].insert_one({
        "ip": ip,
        "song_id": song_id,
        "vote": vote,
        "rating": rating_value,
        "updated_at": int(time.time())
    })

    # Trigger ID3 writeback
    background_tasks.add_task(write_metadata_to_id3, song_id)
    
    # Trigger Playlist Curation (Fetch new average first)
    updated_doc = ratings_col.find_one({"_id": song_id})
    if updated_doc:
         avg = updated_doc.get("average", 0.0)
         background_tasks.add_task(sync_rating_to_playlist, song_id, avg)

    return {
        "status": "ok",
        "song_id": song_id,
        "vote": vote,
        "rating": rating_value,
        "ratings": new_counts,
    }


@app.get("/ratings")
def get_all_ratings():
    # Fetch all ratings from DB
    cursor = ratings_col.find({})
    results = {}
    for doc in cursor:
        song_id = doc["_id"]
        dist = doc.get("distribution", {})
        normalized_dist = {str(k): dist.get(str(k), 0) for k in range(1, 6)}
        
        results[song_id] = {
            "like": doc.get("like", 0),
            "dislike": doc.get("dislike", 0),
            "neutral": doc.get("neutral", 0),
            "distribution": normalized_dist,
            "total": doc.get("total", 0),
            "average": doc.get("average", 0.0),
            "updated_at": doc.get("updated_at", 0),
        }
    return results


@app.get("/moods")
def get_all_moods():
    # Fetch all mood data from DB
    cursor = moods_col.find({})
    results = {}
    for doc in cursor:
        song_id = doc["_id"]
        results[song_id] = {
            "title": doc.get("title", ""),
            "artist": doc.get("artist", ""),
            "moods": doc.get("moods", {}),
            "genres": doc.get("genres", {}),
            "top_mood": doc.get("top_mood"),
            "top_genre": doc.get("top_genre"),
            "total_votes": doc.get("total_votes", 0),
            "updated_at": doc.get("updated_at", 0),
        }
    return results


@app.post("/mood-tag")
async def tag_mood(request: Request, background_tasks: BackgroundTasks):
    try:
        payload = await request.json()
    except json.JSONDecodeError:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON payload."})

    song_id = str(payload.get("song_id", "")).strip()
    mood = str(payload.get("mood", "")).strip().lower()
    genre = str(payload.get("genre", "")).strip().lower()
    
    if not song_id:
        return JSONResponse(status_code=400, content={"error": "song_id is required."})

    if not mood and not genre:
        return JSONResponse(status_code=400, content={"error": "At least one of mood or genre is required."})

    valid_moods = {"energetic", "chill", "dark", "euphoric", "melancholic", "groovy", "hypnotic", "aggressive", "trippy", "warm"}
    valid_genres = {
        "house", "techno", "trance", "dnb", "dubstep", "ambient", "downtempo", 
        "hardstyle", "psytrance", "garage", "disco", "synthwave", "lofi", "idm", 
        "electro", "breakbeat", "jungle", "minimal", "deep-house", "tech-house"
    }

    if mood and mood not in valid_moods:
        return JSONResponse(status_code=400, content={"error": f"Invalid mood. Must be one of {valid_moods}"})
    
    if genre and genre not in valid_genres:
        return JSONResponse(status_code=400, content={"error": f"Invalid genre. Must be one of {valid_genres}"})

    # Update DB
    update_ops = {
        "$set": {
            "updated_at": int(time.time()),
            "title": payload.get("title", ""),
            "artist": payload.get("artist", "")
        },
        "$inc": {
            "total_votes": 1
        }
    }
    
    if mood:
        update_ops["$inc"][f"moods.{mood}"] = 1
    if genre:
        update_ops["$inc"][f"genres.{genre}"] = 1
    
    entry = moods_col.find_one_and_update(
        {"_id": song_id},
        update_ops,
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    
    # Calculate top mood
    moods = entry.get("moods", {})
    if moods:
        top_mood = max(moods, key=moods.get)
        moods_col.update_one({"_id": song_id}, {"$set": {"top_mood": top_mood}})
        entry["top_mood"] = top_mood

    # Calculate top genre
    genres = entry.get("genres", {})
    if genres:
        top_genre = max(genres, key=genres.get)
        moods_col.update_one({"_id": song_id}, {"$set": {"top_genre": top_genre}})
        entry["top_genre"] = top_genre

    # Trigger ID3 writeback
    background_tasks.add_task(write_metadata_to_id3, song_id)
    background_tasks.add_task(sync_mood_to_playlist, song_id, mood)

    # Flattened response for easier frontend consumption
    return {
        "status": "ok",
        "song_id": song_id,
        "mood": mood,
        "genre": genre,
        "moods": entry.get("moods", {}),
        "genres": entry.get("genres", {}),
        "top_mood": entry.get("top_mood"),
        "top_genre": entry.get("top_genre"),
        "total_votes": entry.get("total_votes", 0)
    }


# ---------------------------------------------------------------------------
# Steering & Automation
# ---------------------------------------------------------------------------

# --- WebSocket Manager ---
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    # Send initial state
    try:
        # Send current steering votes
        votes = get_current_steering_votes()
        await websocket.send_json({"type": "steering_update", "votes": votes})
    except:
        pass
        
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# --- End WebSocket Manager ---

# Steering State (In-Memory for now, could be DB)
current_steering_votes = {
    "energetic": 0,
    "chill": 0,
    "groovy": 0,
    "dark": 0
}

def get_current_steering_votes():
    return current_steering_votes

@app.post("/vote-next")
async def vote_next_vibe(request: Request):
    """
    Community Vote for the next vibe.
    """
    try:
        payload = await request.json()
    except json.JSONDecodeError:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON payload."})

    vote = payload.get("vote", "").lower().strip()
    if vote not in current_steering_votes:
        return JSONResponse(status_code=400, content={"error": "Invalid vote option."})

    # Increment vote
    current_steering_votes[vote] += 1
    
    # Broadcast update
    await manager.broadcast({
        "type": "steering_update",
        "votes": current_steering_votes
    })
    
    # Get prediction for this mood
    prediction = predict_next_track_for_mood(vote)

    return {
        "status": "ok",
        "votes": current_steering_votes,
        "prediction": prediction
    }

def predict_next_track_for_mood(mood: str):
    """
    Find the likely next track for a given mood based on ratings.
    """
    # Find candidate songs with this top_mood, sorted by rating
    # Exclude recently played would be ideal, but for now just raw rating
    pipeline = [
        {"$match": {"top_mood": mood}},
        {"$sort": {"average": -1}}, # Highest rated first
        {"$limit": 1}
    ]
    
    # We need to join ratings_col and moods_col if they are separate?
    # In this codebase:
    # ratings_col has 'average'
    # moods_col has 'top_mood', 'title', 'artist'
    # This is tricky if they are separate.
    # Let's assume write_metadata_to_id3 or similar syncs them, 
    # OR we query moods_col and then verify rating.
    
    # Simplification: Query moods_col for the mood, then get title/artist.
    # To get "best", we'd need the rating.
    # Let's query moods_col, sample 1 for variety or use a known 'best'.
    
    candidate = moods_col.find_one({"top_mood": mood}) # Just get one for now to prove concept
    
    if candidate:
        return {
            "title": candidate.get("title", "Unknown"),
            "artist": candidate.get("artist", "Unknown"),
            "art": "" # Future: get art
        }
    return None

@app.post("/control/steer")
async def set_steering(request: Request, current_user: User = Depends(get_current_active_user)):
    """
    Set the global steering mode for the radio (Admin Override).
    """
    try:
        payload = await request.json()
    except json.JSONDecodeError:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON payload."})
        
    mode = payload.get("mode", "auto")
    target = payload.get("target")
    
    set_steering_state(mode, target)
    
    await manager.broadcast({
        "type": "control_update",
        "mode": mode,
        "target": target
    })
    
    return {"status": "ok", "mode": mode, "target": target}



@app.post("/control/vote-next")
async def vote_next_steering(request: Request):
    """
    Community voting for the next vibe.
    payload: { "vote": "energetic" }
    """
    # Rate Limit
    forwarded = request.headers.get("X-Forwarded-For")
    ip = forwarded.split(",")[0] if forwarded else request.client.host
    now = int(time.time())
    
    # Check rate limit (using a simplified method since I can't inject global easily in this tool call sequence)
    # Using the steering_votes_col to check recent votes from this IP
    recent_vote = steering_votes_col.find_one({
        "ip": ip,
        "timestamp": {"$gt": now - 5}
    })
    
    if recent_vote:
         return JSONResponse(status_code=429, content={"error": "Too fast (5s cooldown)"})

    try:

        payload = await request.json()
    except json.JSONDecodeError:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON payload."})
        
    vote = payload.get("vote", "").lower().strip()
    if not vote:
        return JSONResponse(status_code=400, content={"error": "Vote required"})
        
    # Record vote
    steering_votes_col.insert_one({
        "vote": vote,
        "timestamp": int(time.time()),
        "ip": request.client.host
    })

    # Broadcast Votes
    cutoff = int(time.time()) - 300 # Last 5 mins
    pipeline = [
        {"$match": {"timestamp": {"$gt": cutoff}}},
        {"$group": {"_id": "$vote", "count": {"$sum": 1}}}
    ]
    results = list(steering_votes_col.aggregate(pipeline))
    stats = {r["_id"]: r["count"] for r in results}
    
    await manager.broadcast({
        "type": "vote_update",
        "stats": stats,
        "total": sum(stats.values())
    })
    
    return {"status": "ok", "voted": vote}

@app.get("/control/steer")
def get_steering():
    return get_steering_state()

@app.get("/control/next-song")
def get_next_song_candidate():
    """
    Returns a candidate song path/ID for Liquidsoap to play next.
    Logic is based on current steering state.
    """
    import random
    state = get_steering_state()
    mode = state["mode"]
    target = state["target"]
    
    query = {}
    
    if mode == "mood" and target:
        # Find songs where this mood is the top mood or has significant votes
        # Using dot notation for nested mood count: moods.energetic
        query = {f"moods.{target}": {"$gt: 0"}}
        # Ideally we want the one where it is the TOP mood
        # But for now, let's just find any compatible song
        query = {"top_mood": target}
        
    elif mode == "rating":
        min_rating = float(target) if target else 4.0
        # Find songs with average rating >= target
        # We need to join with ratings collection ideally, but we don't have joins here easily in simple find
        # For now, let's assume we might denormalize rating into mood doc or query ratings first
        # Let's query ratings collection first
        high_rated_ids = [doc["_id"] for doc in ratings_col.find({"average": {"$gte": min_rating}}).limit(200)]
        query = {"_id": {"$in": high_rated_ids}}
        
    # Default/Auto: Random from library (or high rated)
    if not query:
        # Fallback to decent songs (e.g. at least one like or neutral)
        pass 

    # Execute Query against Moods collection (which holds metadata)
    # We limit to 100 candidates and pick random to ensure variety
    candidates = list(moods_col.find(query).limit(100))
    
    if not candidates:
        # Fallback if specific query fails: Random song
        candidates = list(moods_col.find({}).limit(100))
        
    if not candidates:
        return JSONResponse(status_code=404, content={"error": "No music found in library."})
        
    selection = random.choice(candidates)
    song_id = selection["_id"]
    
    # Get file path
    # We could call AzuraCast API to get path, but that's slow.
    # We should have the path from ID3 scan or sync.
    # Assuming we can trust AzuraCast ID or we need to look it up.
    # Current Issue: We don't store "Path" in moods_col.
    # We need to fetch it.
    
    # Fetch from AzuraCast API
    # Return string for liquidsoap
    return {
        "song_id": song_id,
        "title": selection.get("title"),
        "artist": selection.get("artist"),
        "reason": f"Matched {mode}={target}"
    }

@app.post("/control/sync-playlists")
async def trigger_playlist_sync(background_tasks: BackgroundTasks):
    """
    Manually triggers a full synchronization of Moods -> AzuraCast Playlists.
    Iterates all songs in the DB with a mood and ensures they are in the correct playlist.
    """
    cursor = mood_col.find({})
    count = 0
    for entry in cursor:
        song_id = entry["_id"]
        mood = entry.get("mood")
        if mood:
            background_tasks.add_task(sync_mood_to_playlist, song_id, mood)
            count += 1
            
    return {"status": "ok", "message": f"Triggered sync for {count} songs. Check logs for progress."}

@app.get("/control/liquidsoap/next", response_class=PlainTextResponse)
async def liquidsoap_next_track():
    """
    Simplified endpoint for Liquidsoap. 
    Returns JUST the absolute file path as raw text.
    """
    candidate = get_next_song_candidate()
    if isinstance(candidate, JSONResponse):
        # Even if it's an error/fallback signal, return path
        return "/var/radio/music/fallback.mp3" 
        
    song_id = candidate["song_id"]
    
    # Resolve Path
    url = f"{AZURACAST_URL}/api/station/1/media/{song_id}"
    headers = {"Authorization": f"Bearer {AZURACAST_API_KEY}"}
    
    async with httpx.AsyncClient(timeout=5, verify=False) as client:
        try:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                rel_path = data.get("path")
                if rel_path:
                    # Construct absolute path expected by Liquidsoap inside the container
                    full_path = str(MUSIC_DIR / rel_path)
                    return full_path
        except:
            pass
            
    return "/var/radio/music/fallback.mp3"


@app.post("/metadata")
async def update_metadata(request: Request):
    try:
        payload = await request.json()
    except json.JSONDecodeError:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON payload."})

    song_id = str(payload.get("song_id", "")).strip()
    title = str(payload.get("title", "")).strip()
    artist = str(payload.get("artist", "")).strip()

    if not song_id:
        return JSONResponse(status_code=400, content={"error": "song_id is required."})
    
    if not title and not artist:
        return JSONResponse(status_code=400, content={"error": "At least one of title or artist is required."})

    # Update DB (moods collection holds metadata for now)
    update_ops = {
        "$set": {
            "updated_at": int(time.time())
        }
    }
    
    if title:
        update_ops["$set"]["title"] = title
    if artist:
        update_ops["$set"]["artist"] = artist

    moods_col.update_one(
        {"_id": song_id},
        update_ops,
        upsert=True
    )

    return {"status": "ok", "song_id": song_id, "title": title, "artist": artist}


# ---------------------------------------------------------------------------
# ID3 helper
# ---------------------------------------------------------------------------


async def write_metadata_to_id3(song_id: str) -> None:
    """
    Write rating AND mood data from MongoDB to MP3 ID3 tags.
    Includes comprehensive logging for debugging and monitoring.
    """
    import logging
    import json
    logger = logging.getLogger(__name__)
    
    logger.info(f"[ID3_WRITE_START] Song ID: {song_id}")
    
    # Fetch rating data
    rating_entry = ratings_col.find_one({"_id": song_id}) or {}
    # Fetch mood data
    mood_entry = moods_col.find_one({"_id": song_id}) or {}
    
    if not rating_entry and not mood_entry:
        logger.warning(f"[ID3_WRITE_SKIP] No metadata in MongoDB for song_id: {song_id}")
        return

    if not AZURACAST_URL or not AZURACAST_API_KEY:
        logger.error("[ID3_WRITE_ERROR] AzuraCast configuration missing (AZURACAST_URL or API_KEY)")
        return

    url = f"{AZURACAST_URL}/api/station/1/media/{song_id}"
    headers = {"Authorization": f"Bearer {AZURACAST_API_KEY}"}
    
    logger.debug(f"[ID3_WRITE_API] Fetching media info from: {url}")

    try:
        async with httpx.AsyncClient(timeout=60, follow_redirects=True, verify=False) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            media = response.json()
            relative_path = media.get("path")
    except httpx.HTTPError as exc:
        logger.error(f"[ID3_WRITE_ERROR] Failed to fetch media info for {song_id}: {exc}")
        return
        
    if not relative_path:
        logger.warning(f"[ID3_WRITE_ERROR] Media path missing in API response for {song_id}")
        return
    
    file_path = MUSIC_DIR / relative_path
    
    if not file_path.exists():
        logger.error(f"[ID3_WRITE_ERROR] File not found at {file_path}")
        return
    
    logger.info(f"[ID3_WRITE_FILE] File exists, loading ID3 tags from {file_path}")

    try:
        audio = ID3(file_path)
    except Exception as exc:
        logger.error(f"[ID3_WRITE_ERROR] Failed to load ID3 tags from {file_path}: {exc}")
        return

    # --- Write RATINGS ---
    if rating_entry:
        audio["TXXX:YOURPARTY_RATING_LIKES"] = TXXX(encoding=3, desc="YOURPARTY_RATING_LIKES", text=str(rating_entry.get("like", 0)))
        audio["TXXX:YOURPARTY_RATING_DISLIKES"] = TXXX(encoding=3, desc="YOURPARTY_RATING_DISLIKES", text=str(rating_entry.get("dislike", 0)))
        audio["TXXX:YOURPARTY_RATING_NEUTRAL"] = TXXX(encoding=3, desc="YOURPARTY_RATING_NEUTRAL", text=str(rating_entry.get("neutral", 0)))
        audio["TXXX:YOURPARTY_RATING_AVG"] = TXXX(encoding=3, desc="YOURPARTY_RATING_AVG", text=str(rating_entry.get("average", 0.0)))
        audio["TXXX:YOURPARTY_RATING_TOTAL"] = TXXX(encoding=3, desc="YOURPARTY_RATING_TOTAL", text=str(rating_entry.get("total", 0)))

        distribution = rating_entry.get("distribution", {})
        for star in range(1, 6):
            count = distribution.get(str(star), 0)
            audio[f"TXXX:YOURPARTY_RATING_STAR_{star}"] = TXXX(encoding=3, desc=f"YOURPARTY_RATING_STAR_{star}", text=str(count))

    # --- Write MOODS & GENRES ---
    if mood_entry:
        top_mood = mood_entry.get("top_mood", "")
        moods_dict = mood_entry.get("moods", {})
        
        if top_mood:
            audio["TXXX:YOURPARTY_MOOD_TOP"] = TXXX(encoding=3, desc="YOURPARTY_MOOD_TOP", text=top_mood)
            # Auch als Standard MOOD Tag schreiben (TMOO) für Kompatibilität
            audio["TMOO"] = TXXX(encoding=3, desc="MOOD", text=top_mood)
            
        # Alle Votes als JSON speichern (für spätere Analyse)
        audio["TXXX:YOURPARTY_MOOD_VOTES"] = TXXX(encoding=3, desc="YOURPARTY_MOOD_VOTES", text=json.dumps(moods_dict))

        # GENRES
        top_genre = mood_entry.get("top_genre", "")
        genres_dict = mood_entry.get("genres", {})
        
        if top_genre:
            from mutagen.id3 import TCON
            audio["TCON"] = TCON(encoding=3, text=top_genre)
            audio["TXXX:YOURPARTY_GENRE_TOP"] = TXXX(encoding=3, desc="YOURPARTY_GENRE_TOP", text=top_genre)
            
        audio["TXXX:YOURPARTY_GENRE_VOTES"] = TXXX(encoding=3, desc="YOURPARTY_GENRE_VOTES", text=json.dumps(genres_dict))

    logger.debug(f"[ID3_WRITE_TAGS] All tags prepared, saving to file...")

    try:
        audio.save(v2_version=3)
        logger.info(f"[ID3_WRITE_SUCCESS] ✅ ID3 tags updated successfully for {song_id}")
    except Exception as exc:
        logger.error(f"[ID3_WRITE_ERROR] ❌ Failed to save ID3 tags to {file_path}: {exc}")


async def add_to_azuracast_playlist(song_id: str, playlist_name: str):
    """
    Generic automation: Ensures playlist exists and adds song to it.
    """
    # 1. Get all playlists (Check existing)
    url = f"{AZURACAST_URL}/api/station/1/playlists"
    headers = {"Authorization": f"Bearer {AZURACAST_API_KEY}"}
    
    playlist_id = None
    
    async with httpx.AsyncClient(timeout=10, verify=False) as client:
        try:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                playlists = resp.json()
                for pl in playlists:
                    if pl["name"] == playlist_name:
                        playlist_id = pl["id"]
                        break
        except Exception as e:
            print(f"[PLAYLIST_SYNC] Error fetching playlists: {e}")
            return

        # Create if missing
        if not playlist_id:
            try:
                create_payload = {
                    "name": playlist_name,
                    "is_enabled": True,
                    "type": "default",
                    "weight": 5,
                    "include_in_requests": True
                }
                resp = await client.post(url, json=create_payload, headers=headers)
                if resp.status_code == 200:
                    new_pl = resp.json()
                    playlist_id = new_pl["id"]
                    print(f"[PLAYLIST_SYNC] Created playlist '{playlist_name}' (ID: {playlist_id})")
            except Exception as e:
                print(f"[PLAYLIST_SYNC] Error creating playlist: {e}")
                return
                
    if not playlist_id:
        return

    # 2. Add song to playlist
    media_url = f"{AZURACAST_URL}/api/station/1/media/{song_id}"
    
    async with httpx.AsyncClient(timeout=10, verify=False) as client:
        try:
            resp = await client.get(media_url, headers=headers)
            if resp.status_code != 200:
                return
            
            media_data = resp.json()
            current_playlists = [p["id"] for p in media_data.get("playlists", [])]
            
            if playlist_id in current_playlists:
                return # Already in playlist
                
            current_playlists.append(playlist_id)
            
            # Update media (Merge Logic)
            media_data["playlists"] = current_playlists
            
            resp = await client.put(media_url, json=media_data, headers=headers)
            if resp.status_code == 200:
                 print(f"[PLAYLIST_SYNC] Added song {song_id} to '{playlist_name}'")
            else:
                 print(f"[PLAYLIST_SYNC] Failed to update media {song_id}: {resp.status_code} {resp.text}")

        except Exception as e:
            print(f"[PLAYLIST_SYNC] Error updating media: {e}")

async def sync_mood_to_playlist(song_id: str, mood: str):
    if mood:
        await add_to_azuracast_playlist(song_id, f"Mood: {mood.capitalize()}")

async def sync_rating_to_playlist(song_id: str, rating: float):
    """
    Automated Curation: High rated songs go to Best Of.
    """
    if rating >= 4.0:
         await add_to_azuracast_playlist(song_id, "YourParty Best Of")


# ---------------------------------------------------------------------------
# Curation Automation Loop
# ---------------------------------------------------------------------------
async def curation_loop():
    print("[CURATOR] Starting Background Curation Loop...")
    while True:
        try:
             # Find all songs with avg rating >= 4.0
             cursor = ratings_col.find({"average": {"$gte": 4.0}})
             for doc in cursor:
                 song_id = doc["_id"]
                 avg = doc.get("average", 0.0)
                 await sync_rating_to_playlist(song_id, avg)
                 await asyncio.sleep(0.1) # Throttle to avoid API spam
        except Exception as e:
             print(f"[CURATOR] Critical Error: {e}")
        
        await asyncio.sleep(3600) # Run every hour

@app.on_event("startup")
async def start_curator():
     asyncio.create_task(curation_loop())


# ---------------------------------------------------------------------------
# Monitoring Metrics
# ---------------------------------------------------------------------------
import asyncio
from prometheus_client import Gauge

# Metric Definitions
PLAYLIST_TRACKS = Gauge('radio_playlist_tracks', 'Number of tracks in playlist', ['name'])
N8N_STATUS = Gauge('radio_n8n_up', 'n8n Automation Status (1=UP)')

async def update_metrics_loop():
    print("[MONITORING] Starting metrics loop...")
    
    # Try to find credentials
    azura_url = os.getenv("AZURA_API_URL", "http://192.168.178.210/api")
    azura_key = os.getenv("YOURPARTY_AZURACAST_API_KEY") or os.getenv("AZURACAST_API_KEY")
    
    # n8n URL
    n8n_url = os.getenv("N8N_API_URL", "http://n8n:5678/healthz")

    while True:
        try:
            async with httpx.AsyncClient(verify=False) as client:
                # 1. AzuraCast Playlists
                if azura_key:
                    headers = {"Authorization": f"Bearer {azura_key}"}
                    try:
                        r = await client.get(f"{azura_url}/station/1/playlists", headers=headers, timeout=10)
                        if r.status_code == 200:
                            data = r.json()
                            if isinstance(data, dict) and 'rows' in data:
                                data = data['rows']
                            
                            if isinstance(data, list):
                                for pl in data:
                                    name = pl.get('name', 'unknown')
                                    count = pl.get('num_songs', pl.get('count', 0))
                                    PLAYLIST_TRACKS.labels(name=name).set(count)
                    except Exception as e:
                         print(f"[MONITORING] AzuraCast Fetch Warn: {e}")
                
                # 2. n8n Status
                try:
                    r = await client.get(n8n_url, timeout=2)
                    N8N_STATUS.set(1 if r.status_code < 500 else 0)
                except:
                    # Fallback to public
                    try:
                        r = await client.get("https://n8n.yourparty.tech/healthz", timeout=2)
                        N8N_STATUS.set(1 if r.status_code < 500 else 0)
                    except:
                        N8N_STATUS.set(0)

        except Exception as e:
            print(f"[MONITORING] Critical Loop Error: {e}")
            
        await asyncio.sleep(60)

@app.on_event("startup")
async def start_metrics_task():
    asyncio.create_task(update_metrics_loop())

