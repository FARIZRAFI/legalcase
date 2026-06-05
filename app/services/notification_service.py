from sqlalchemy.orm import Session
from app.models.notification_model import Notification
from app.core.websocket import manager

async def create_notification(db: Session, user_id: int, message: str):
    """
    Creates a database record for a notification and immediately
    pushes it out via WebSockets if the user is online.
    """
    new_notif = Notification(user_id=user_id, content=message, is_read=False)
    db.add(new_notif)
    db.commit()
    db.refresh(new_notif)

    # Payload matches the dictionary format expected by the updated connection manager
    await manager.send_personal_message({
        "id": new_notif.id,
        "content": message,
        "is_read": False
    }, user_id)
    
    return new_notif