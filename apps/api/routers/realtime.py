import logging
from typing import List, Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from state import state

router = APIRouter()
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # rooms maps station_id (str) -> list of WebSocket connections
        self.rooms: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, station_id: str):
        await websocket.accept()
        if station_id not in self.rooms:
            self.rooms[station_id] = []
        self.rooms[station_id].append(websocket)

    def disconnect(self, websocket: WebSocket, station_id: str):
        if station_id in self.rooms:
            if websocket in self.rooms[station_id]:
                self.rooms[station_id].remove(websocket)
            if not self.rooms[station_id]:
                del self.rooms[station_id]

    async def broadcast(self, message: Dict[str, Any], station_id: str = "1"):
        if station_id in self.rooms:
            for connection in self.rooms[station_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to station {station_id}: {e}")

manager = ConnectionManager()

@router.websocket("/ws/{station_id}")
async def websocket_endpoint(websocket: WebSocket, station_id: str):
    await manager.connect(websocket, station_id)
    logger.info(f"New WebSocket connection established for station {station_id}")
    try:
        # 1. Send immediate "Now Playing" from state
        sid_int = int(station_id) if station_id.isdigit() else 1
        current_track = state.now_playing.get(sid_int, {
            "title": "Station Online",
            "artist": "YourParty Radio",
            "art": "https://radio.yourparty.tech/wp-content/uploads/2023/11/station_logo.png",
            "rating": {"average": 0.0}
        })
        
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
        manager.disconnect(websocket, station_id)
        logger.info(f"WebSocket disconnected from station {station_id}")
    except Exception as e:
        logger.error(f"WebSocket Error for station {station_id}: {e}")
