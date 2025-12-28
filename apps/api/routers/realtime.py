import logging
from typing import List, Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from state import state

router = APIRouter()
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting: {e}")

manager = ConnectionManager()

@router.websocket("/ws/{station_id}")
async def websocket_endpoint(websocket: WebSocket, station_id: str):
    await manager.connect(websocket)
    logger.info("New WebSocket connection established")
    try:
        # 1. Send immediate "Now Playing" (Mock or Real)
        current_track = {
            "title": "Station Online",
            "artist": "YourParty Radio",
            "art": "https://placehold.co/600x600/10b981/ffffff?text=ON+AIR",
            "rating": {"average": 5.0} # Default
        }
        
        # Try to get real info from state
        if state.now_playing and state.now_playing.get('title') != "Station Online":
             current_track = state.now_playing
             
        await websocket.send_json({
            "type": "song",
            "data": current_track
        })

        # 2. Keep alive
        while True:
            # Wait for any message (ping/pong)
            data = await websocket.receive_text()
            # We could handle incoming 'vibe' votes here
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket Error: {e}")
