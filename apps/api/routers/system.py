from fastapi import APIRouter, Response
from state import state
from datetime import datetime
import time

router = APIRouter()

# Track startup time for uptime calculation
_startup_time = time.time()
__version__ = "1.0.0"

@router.get("/")
async def root():
    return {"message": "Music Library Automation API is running", "version": __version__}

@router.get("/status")
async def public_status(station_id: int = 1):
    """Public status endpoint compatible with frontend polling."""
    return {
        "now_playing": {
            "song": state.now_playing.get(station_id, {})
        },
        "listeners": {"total": 0}, 
        "playing_next": {"song": {"title": "Coming Soon", "artist": "YourParty"}},
        "steering": state.steering_status.get(station_id, {})
    }

@router.get("/debug/status")
async def debug_status(station_id: int = 1):
    """Debug endpoint to check internal state."""
    return {
        "now_playing": state.now_playing.get(station_id, {}),
        "mongo_connected": state.mongo_client is not None,
        "loop_running": True
    }

@router.get("/debug/ping")
async def debug_ping():
    return {"status": "pong", "mongo": state.mongo_client is not None}

@router.get("/health")
async def health_check(response: Response):
    """
    Comprehensive health check for uptime monitoring.
    Returns 200 if all critical services are reachable, 503 if degraded.
    """
    uptime_seconds = int(time.time() - _startup_time)
    
    checks = {
        "api": "ok",
        "mongodb": "unknown",
        "azuracast": "unknown",
    }
    
    # Check MongoDB
    try:
        if state.mongo_client and state.mongo_client.db:
            state.mongo_client.db.command("ping")
            checks["mongodb"] = "ok"
        else:
            checks["mongodb"] = "not_configured"
    except Exception as e:
        checks["mongodb"] = f"error: {str(e)[:50]}"
    
    # Check AzuraCast (via cached state - if we have recent now_playing data)
    np = state.now_playing.get(1, {})
    if np and np.get("title"):
        checks["azuracast"] = "ok"
    else:
        checks["azuracast"] = "no_data"
    
    # Overall status
    critical_ok = checks["mongodb"] == "ok"
    all_ok = critical_ok and checks["azuracast"] == "ok"
    
    status = "healthy" if all_ok else ("degraded" if critical_ok else "unhealthy")
    
    # Set HTTP status code
    if status == "unhealthy":
        response.status_code = 503
    elif status == "degraded":
        response.status_code = 200  # Still serving, but not fully operational
    
    return {
        "status": status,
        "version": __version__,
        "uptime_seconds": uptime_seconds,
        "uptime_human": f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

