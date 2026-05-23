from app.models.notification_model import Notification

from app.routes.notification_routes import (
    broadcast_notification
)



async def create_system_notification(

    db,

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