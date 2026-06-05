from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from typing import Dict, List
import json

router = APIRouter(
    prefix="/ws",
    tags=["WebSocket"]
)

class ConnectionManager:
    def __init__(self):
        # Map user_id (int) to a list of their active WebSockets
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
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
        """Matches your notification_service.py call signature"""
        if user_id in self.active_connections:
            # Convert dict to JSON string before sending
            json_data = json.dumps(message)
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(json_data)
                except Exception:
                    # Handle dead connections gracefully
                    pass

    async def broadcast(self, message: str):
        for user_id, connections in list(self.active_connections.items()):
            for connection in connections:
                try:
                    await connection.send_text(message)
                except Exception:
                    self.disconnect(connection, user_id)

manager = ConnectionManager()

# Accept user_id as a query parameter from the frontend to identify the user
@router.websocket("/notifications")
async def websocket_endpoint(websocket: WebSocket, user_id: int = Query(...)):
    # Crucial: This overrides the strict origin check to stop the 403 error
    # Only use "*" in development; narrow it down to your domain in production
    origin = websocket.headers.get("origin")
    
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)