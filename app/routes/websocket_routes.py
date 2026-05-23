from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect
)

from typing import List


router = APIRouter(
    tags=["WebSocket"]
)



# =========================
# CONNECTION MANAGER
# =========================

class ConnectionManager:

    def __init__(self):

        self.active_connections: List[
            WebSocket
        ] = []



    # CONNECT
    async def connect(

        self,

        websocket: WebSocket
    ):

        await websocket.accept()

        self.active_connections.append(
            websocket
        )

        print(
            "WebSocket Connected"
        )



    # DISCONNECT
    def disconnect(

        self,

        websocket: WebSocket
    ):

        if websocket in self.active_connections:

            self.active_connections.remove(
                websocket
            )

            print(
                "WebSocket Disconnected"
            )



    # SEND PERSONAL MESSAGE
    async def send_personal_message(

        self,

        message: str,

        websocket: WebSocket
    ):

        await websocket.send_text(
            message
        )



    # BROADCAST
    async def broadcast(

        self,

        message: str
    ):

        disconnected_clients = []


        for connection in self.active_connections:

            try:

                await connection.send_text(
                    message
                )

            except Exception:

                disconnected_clients.append(
                    connection
                )


        # REMOVE DEAD CONNECTIONS
        for dead_connection in disconnected_clients:

            self.disconnect(
                dead_connection
            )



# GLOBAL MANAGER
manager = ConnectionManager()



# =========================
# WEBSOCKET ENDPOINT
# =========================

@router.websocket(
    "/notifications/ws"
)
async def websocket_endpoint(

    websocket: WebSocket
):

    await manager.connect(
        websocket
    )

    try:

        while True:

            # KEEP CONNECTION ALIVE
            await websocket.receive_text()

    except WebSocketDisconnect:

        manager.disconnect(
            websocket
        )



# =========================
# BROADCAST FUNCTION
# =========================

async def broadcast_notification(
    message: str
):

    await manager.broadcast(
        message
    )