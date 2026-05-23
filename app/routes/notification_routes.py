from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect
)

from sqlalchemy.orm import Session

from app.database import SessionLocal

from app.models.notification_model import Notification

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
# WEBSOCKET CONNECTIONS
# =========================

active_connections = []



@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket
):

    await websocket.accept()

    active_connections.append(websocket)

    try:

        while True:

            await websocket.receive_text()

    except WebSocketDisconnect:

        active_connections.remove(websocket)



# =========================
# BROADCAST FUNCTION
# =========================

async def broadcast_notification(
    message: str
):

    disconnected = []

    for connection in active_connections:

        try:

            await connection.send_text(
                message
            )

        except:

            disconnected.append(
                connection
            )

    for connection in disconnected:

        if connection in active_connections:

            active_connections.remove(
                connection
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


    if notification:

        notification.is_read = True

        db.commit()

        db.refresh(notification)


    return {

        "message":
        "Notification marked as read"

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


    # LIVE BROADCAST
    await broadcast_notification(

        f"{notification.type}: {notification.message}"
    )

    return new_notification



# =========================
# HEARING REMINDERS
# =========================

@router.post("/send-hearing-reminders")
def send_hearing_reminders(

    db: Session = Depends(get_db)

):

    return create_hearing_reminders(db)



# =========================
# AUTO CREATE FUNCTIONS
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


    # LIVE PUSH
    await broadcast_notification(

        f"{title} - {message}"
    )

    return notification