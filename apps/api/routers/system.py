from fastapi import APIRouter
from state import state
from datetime import datetime

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

@router.get("/health")
async def health_check():
    """
    Comprehensive health check for uptime monitoring.
    Returns 200 if all critical services are reachable.
    """
    checks = {
        "api": "ok",
        "mongo": "unknown",
        "azura": "unknown",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Check MongoDB
    try:
        if state.mongo_client:
            # Quick ping
            state.mongo_client.db.command("ping")
            checks["mongo"] = "ok"
        else:
            checks["mongo"] = "not_configured"
    except Exception as e:
        checks["mongo"] = f"error: {str(e)[:50]}"
    
    # Check AzuraCast (via cached state)
    if state.now_playing and state.now_playing.get("title"):
        checks["azura"] = "ok"
    else:
        checks["azura"] = "no_data"
    
    # Overall status
    all_ok = checks["mongo"] == "ok" and checks["azura"] == "ok"
    checks["status"] = "healthy" if all_ok else "degraded"
    
    return checks

