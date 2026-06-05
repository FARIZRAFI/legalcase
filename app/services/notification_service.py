from app.models.notification_model import Notification
from app.core.websocket import broadcast_notification  # Clean, unidirectional flow

async def create_system_notification(db, user_id: int, title: str, message: str, notification_type: str):
    try:
        notification = Notification(user_id=user_id, title=title, message=message, type=notification_type)
        db.add(notification)
        db.commit()
        db.refresh(notification)

        # Triggers broadcast directly without circular dependencies
        try:
            await broadcast_notification(title, message, notification_type)
        except Exception as ws_err:
            print(f"WebSocket broadcast failed: {str(ws_err)}")

        return notification
    except Exception as e:
        db.rollback()
        return None

def create_system_notification_sync(db, user_id: int, title: str, message: str, notification_type: str):
    try:
        notification = Notification(user_id=user_id, title=title, message=message, type=notification_type)
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification
    except Exception as e:
        db.rollback()
        return None