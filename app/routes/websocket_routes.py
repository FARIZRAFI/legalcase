from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(
    tags=["WebSocket"]
)


connected_clients = []


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()

    connected_clients.append(websocket)

    try:

        while True:

            data = await websocket.receive_text()

            for client in connected_clients:

                await client.send_text(
                    f"Message: {data}"
                )

    except WebSocketDisconnect:

        connected_clients.remove(websocket)