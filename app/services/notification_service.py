from sqlalchemy.orm import Session
from app.models.notification_model import Notification
from app.core.websocket import manager

# Ensure this exact function name exists at the top level of the file
async def create_notification(db: Session, user_id: int, message: str):
    new_notif = Notification(user_id=user_id, content=message, is_read=False)
    db.add(new_notif)
    db.commit()
    db.refresh(new_notif)

    await manager.send_personal_message({
        "id": new_notif.id,
        "content": message,
        "is_read": False
    }, user_id)
    
    return new_notif