# app/core/websocket.py
from fastapi import WebSocket
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_json(self, data: dict):
        disconnected_clients = []
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception:
                disconnected_clients.append(connection)
        for dead_connection in disconnected_clients:
            self.disconnect(dead_connection)

# The single, unified global instance shared across the entire system
manager = ConnectionManager()

async def broadcast_notification(title: str, message: str, notification_type: str = "General"):
    payload = {"title": title, "message": message, "type": notification_type}
    await manager.broadcast_json(payload)