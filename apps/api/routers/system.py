from fastapi import APIRouter
from state import state

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Music Library Automation API is running"}

@router.get("/status")
async def public_status():
    """Public status endpoint compatible with frontend polling."""
    return {
        "now_playing": {
            "song": state.now_playing
        },
        "listeners": {"total": 0}, 
        "playing_next": {"song": {"title": "Coming Soon", "artist": "YourParty"}},
        "steering": state.steering_status # Add steering info for dashboard/frontend
    }

@router.get("/debug/status")
async def debug_status():
    """Debug endpoint to check internal state."""
    return {
        "now_playing": state.now_playing,
        "mongo_connected": state.mongo_client is not None,
        "loop_running": True
    }

@router.get("/debug/ping")
async def debug_ping():
    return {"status": "pong", "mongo": state.mongo_client is not None}
