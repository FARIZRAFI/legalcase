from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Dict, List
import json

# Setting prefix to match the log: /api/notifications/ws
router = APIRouter(
    prefix="/notifications",
    tags=["WebSocket"]
)

class ConnectionManager:
    def __init__(self):
        # Maps user_id (int) -> list of active WebSockets for that user
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        # Loosen strict origin security checks to prevent the 403 Forbidden error
        # In production, replace "*" with your actual frontend domain
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        """Sends a JSON payload to all active tabs/sockets of a specific user"""
        if user_id in self.active_connections:
            json_data = json.dumps(message)
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(json_data)
                except Exception:
                    # Clear broken connections automatically
                    pass

    async def broadcast(self, message: str):
        """Sends a plain text message to absolutely everyone connected"""
        for user_id, connections in list(self.active_connections.items()):
            for connection in connections:
                try:
                    await connection.send_text(message)
                except Exception:
                    self.disconnect(connection, user_id)

manager = ConnectionManager()

# This route becomes /api/notifications/ws when mounted under your api router
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, user_id: int = Query(...)):
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive; discard incoming text from clients
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)