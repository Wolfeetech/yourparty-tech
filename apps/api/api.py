import os
import sys
import logging
import asyncio
import httpx
from datetime import timedelta
from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from limiter import limiter

# Fix Path for Imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables early
base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, '.env'))
print(f"DEBUG: JWT_SECRET_KEY starts with: {os.getenv('JWT_SECRET_KEY', 'MISSING')[:4]}")

# Import State
from state import state, AppState

# Import Routers
from routers import system, library, interactive, realtime

# Import Helpers
from azuracast_client import AzuraCastClient
from mongo_client import MongoDatabaseClient
from track_matcher import TrackMatcher
from library_service import get_library_service
from playlist_service import PlaylistService
from mood_scheduler import schedule_mood_queue_worker

# Auth Imports
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status
from auth import Token, User, create_access_token, get_current_active_user, users_db, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES

# ========== FEATURE FLAGS ==========
FEATURE_MOOD_VOTES = os.getenv("FEATURE_MOOD_VOTES", "true").lower() == "true"
FEATURE_MOOD_SYNC = os.getenv("FEATURE_MOOD_SYNC", "false").lower() == "true"
FEATURE_MOOD_AUTODJ = os.getenv("FEATURE_MOOD_AUTODJ", "false").lower() == "true"
MOOD_CYCLE_SECONDS = int(os.getenv("MOOD_CYCLE_SECONDS", "300"))
AZURACAST_VERIFY_SSL = os.getenv("AZURACAST_VERIFY_SSL", "false").lower() == "true"

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Music Library Automation API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "path": str(request.url.path)},
    )

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourparty.tech",
        "https://www.yourparty.tech",
        "https://radio.yourparty.tech",
        "https://control.yourparty.tech",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# INCLUDE ROUTERS
app.include_router(system.router)
app.include_router(library.router)
app.include_router(interactive.router)
app.include_router(realtime.router)

# AUTH ENDPOINTS

@app.post("/token", response_model=Token)
@limiter.limit("5/minute")
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = User(**user_dict)
    if not verify_password(form_data.password, user_dict["hashed_password"]):
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


# BACKGROUND TASKS

async def public_status_loop():
    """Poll AzuraCast public API for Metadata (Multiple Stations)."""
    logger.info("Public Status Loop Started.")
    stations = [1, 2]  # Active stations
    
    while True:
        try:
            azura_base = os.getenv("AZURACAST_URL")
            if not azura_base:
                await asyncio.sleep(10)
                continue
            
            for sid in stations:
                try:
                    # Use public endpoint
                    url = f"{azura_base}/api/nowplaying/{sid}" 
                    
                    async with httpx.AsyncClient(verify=AZURACAST_VERIFY_SSL, follow_redirects=True) as client:
                        try:
                            resp = await client.get(url, timeout=5.0)
                        except httpx.ConnectError:
                            url = azura_base.replace('http://', 'https://') + f"/api/nowplaying/{sid}"
                            resp = await client.get(url, timeout=5.0)
                        except Exception as e:
                            logger.error(f"Connection error to AzuraCast for station {sid}: {e}")
                            resp = None

                        if resp and resp.status_code == 200:
                            data = resp.json()
                            np = data.get('now_playing', {}).get('song', {})
                            
                            # Update Stream URL for this station
                            for mount in data.get('station', {}).get('mounts', []):
                                 if mount.get('is_default'):
                                     stream_url = mount.get('url', '')
                                     if stream_url.startswith('http://'):
                                         stream_url = stream_url.replace('http://', 'https://')
                                     state.stream_urls[sid] = stream_url

                            current_track = {
                                "title": np.get('title', ''),
                                "artist": np.get('artist', ''),
                                "album": np.get('album', ''),
                                "art": np.get('art', ''), 
                                "id": str(np.get('id', '')), 
                                "duration": np.get('duration', 0),
                                "genre": np.get('genre', '')
                            }

                            # Fix Art URL
                            if '192.168' in current_track['art']:
                                current_track['art'] = "https://radio.yourparty.tech/wp-content/uploads/2023/11/station_logo.png"

                            # Fallbacks
                            if not current_track['title'] or not current_track['artist']:
                                full_text = np.get('text', '')
                                if ' - ' in full_text:
                                    parts = full_text.split(' - ', 1)
                                    if not current_track['artist']: current_track['artist'] = parts[0]
                                    if not current_track['title']: current_track['title'] = parts[1]
                                elif full_text and not current_track['title']:
                                     current_track['title'] = full_text
                            
                            if not current_track['title']: current_track['title'] = 'Station Online'
                            if not current_track['artist']: current_track['artist'] = 'YourParty Radio'
                            
                            # Inject Mongo Data
                            if state.mongo_client and current_track['id']:
                                 song_id = current_track['id']
                                 rating_data = state.mongo_client.get_track_rating(song_id=song_id, station_id=sid)
                                 current_track['rating'] = rating_data or {"average": 0.0, "total": 0}
                                 
                                 mood_data = state.mongo_client.get_song_moods(song_id)
                                 current_track['top_mood'] = mood_data.get('top_mood')

                            state.now_playing[sid] = current_track
                            
                            # Broadcast to WS for this station
                            await realtime.manager.broadcast({
                                "type": "song",
                                "song": current_track
                            }, station_id=str(sid))
                except Exception as e:
                    logger.error(f"Error polling station {sid}: {e}")
                    
        except Exception as e:
            logger.error(f"Polling Main Loop Error: {e}")
            
        await asyncio.sleep(2.0)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Radio API (Modularized)...")
    
    # Initialize AzuraCast
    azura_url = os.getenv("AZURACAST_URL")
    azura_key = os.getenv("AZURACAST_API_KEY")
    if azura_url and azura_key:
        try:
            state.azura_client = AzuraCastClient(azura_url, azura_key, 1)
            logger.info("Global AzuraCast Client initialized.")
        except Exception as e:
            logger.error(f"Failed to init AzuraCast client: {e}")

    logger.info(f"Feature Flags: MOOD_VOTES={FEATURE_MOOD_VOTES}, MOOD_AUTODJ={FEATURE_MOOD_AUTODJ}")
    
    # Start Polling
    asyncio.create_task(public_status_loop())

    # Initialize Mongo
    try:
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            user = os.getenv("MONGO_INITDB_ROOT_USERNAME", "root")
            pwd = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "")
            host = os.getenv("MONGO_HOST", "localhost")
            port = os.getenv("MONGO_PORT", "27017")
            if user and pwd:
                mongo_uri = f"mongodb://{user}:{pwd}@{host}:{port}/"
            else:
                mongo_uri = f"mongodb://{host}:{port}/"
        
        state.mongo_client = MongoDatabaseClient(mongo_uri)
        state.track_matcher = TrackMatcher(state.mongo_client)
        state.library_service = get_library_service(state.mongo_client)
        
        # Initialize Playlist Service (requires both)
        if state.azura_client:
            state.playlist_service = PlaylistService(state.mongo_client, state.azura_client)
        
        logger.info("Connected to MongoDB & Services Initialized.")
    except Exception as e:
        logger.error(f"Failed to connect to Mongo: {e}")

    # Start Mood Auto-DJ
    if FEATURE_MOOD_AUTODJ and state.mongo_client and state.azura_client:
        try:
            logger.info(f"Starting Mood Auto-DJ (cycle: {MOOD_CYCLE_SECONDS}s)...")
            asyncio.create_task(schedule_mood_queue_worker(
                state.mongo_client, 
                state.azura_client,
                steering_status_map=state.steering_status
            ))
        except Exception as e:
            logger.error(f"Failed to start Mood Auto-DJ: {e}")
