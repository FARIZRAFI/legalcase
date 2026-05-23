from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
    HTTPException
)

from sqlalchemy.orm import Session

from typing import List

from app.database import SessionLocal

from app.models.notification_model import (
    Notification
)

from app.schemas.notification_schema import (
    NotificationCreate
)

from app.services.reminder_service import (
    create_hearing_reminders
)

from app.services.auth_service import (
    verify_token
)


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)



# =========================
# DATABASE CONNECTION
# =========================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()



# =========================
# WEBSOCKET MANAGER
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
            "Notification WebSocket Connected"
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
                "Notification WebSocket Disconnected"
            )



    # SEND MESSAGE
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

@router.websocket("/ws")
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



# =========================
# GET ALL NOTIFICATIONS
# =========================

@router.get("/")
def get_notifications(

    db: Session = Depends(get_db),

    user_data: dict = Depends(verify_token)

):

    notifications = db.query(
        Notification
    ).order_by(
        Notification.id.desc()
    ).all()

    return notifications



# =========================
# GET SINGLE NOTIFICATION
# =========================

@router.get("/{notification_id}")
def get_notification(

    notification_id: int,

    db: Session = Depends(get_db),

    user_data: dict = Depends(verify_token)
):

    notification = db.query(
        Notification
    ).filter(

        Notification.id == notification_id

    ).first()


    if not notification:

        raise HTTPException(

            status_code=404,

            detail="Notification not found"
        )


    return notification



# =========================
# MARK AS READ
# =========================

@router.put("/{notification_id}")
def mark_notification_read(

    notification_id: int,

    db: Session = Depends(get_db)

):

    notification = db.query(
        Notification
    ).filter(

        Notification.id == notification_id

    ).first()


    if not notification:

        raise HTTPException(

            status_code=404,

            detail="Notification not found"
        )


    notification.is_read = True

    db.commit()

    db.refresh(notification)


    return {

        "message":
        "Notification marked as read"
    }



# =========================
# DELETE NOTIFICATION
# =========================

@router.delete("/{notification_id}")
def delete_notification(

    notification_id: int,

    db: Session = Depends(get_db),

    user_data: dict = Depends(verify_token)
):

    notification = db.query(
        Notification
    ).filter(

        Notification.id == notification_id

    ).first()


    if not notification:

        raise HTTPException(

            status_code=404,

            detail="Notification not found"
        )


    db.delete(notification)

    db.commit()


    return {

        "message":
        "Notification deleted successfully"
    }



# =========================
# CREATE NOTIFICATION
# =========================

@router.post("/")
async def create_notification(

    notification: NotificationCreate,

    db: Session = Depends(get_db)

):

    new_notification = Notification(

        user_id=notification.user_id,

        title=notification.title,

        message=notification.message,

        type=notification.type
    )

    db.add(new_notification)

    db.commit()

    db.refresh(new_notification)



    # LIVE WEBSOCKET PUSH
    await broadcast_notification(

        f"{notification.title} - {notification.message}"
    )


    return new_notification



# =========================
# SEND HEARING REMINDERS
# =========================

@router.post("/send-hearing-reminders")
def send_hearing_reminders(

    db: Session = Depends(get_db)

):

    return create_hearing_reminders(db)



# =========================
# SYSTEM NOTIFICATION
# =========================

async def create_system_notification(

    db: Session,

    user_id: int,

    title: str,

    message: str,

    notification_type: str
):

    notification = Notification(

        user_id=user_id,

        title=title,

        message=message,

        type=notification_type
    )

    db.add(notification)

    db.commit()

    db.refresh(notification)



    # LIVE WEBSOCKET PUSH
    await broadcast_notification(

        f"{title} - {message}"
    )


    return notification