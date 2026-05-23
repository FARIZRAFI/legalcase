from app.models.notification_model import (
    Notification
)



# =========================
# CREATE SYSTEM NOTIFICATION
# =========================

async def create_system_notification(

    db,

    user_id: int,

    title: str,

    message: str,

    notification_type: str
):

    try:


        notification = Notification(

            user_id=user_id,

            title=title,

            message=message,

            type=notification_type
        )



        db.add(notification)

        db.commit()

        db.refresh(notification)



        print(
            f"Notification created: {title}"
        )



        # =========================
        # SAFE WEBSOCKET IMPORT
        # =========================

        try:

            from app.routes.notification_routes import (
                broadcast_notification
            )



            await broadcast_notification(

                f"{title} - {message}"
            )



        except Exception as websocket_error:


            print(
                "WebSocket broadcast failed:"
            )

            print(str(websocket_error))



        return notification



    except Exception as e:


        db.rollback()



        print(
            "Notification creation failed:"
        )

        print(str(e))



        return None



# =========================
# BULK NOTIFICATIONS
# =========================

async def create_bulk_notifications(

    db,

    user_ids: list,

    title: str,

    message: str,

    notification_type: str
):

    created_notifications = []



    try:


        for user_id in user_ids:


            notification = Notification(

                user_id=user_id,

                title=title,

                message=message,

                type=notification_type
            )



            db.add(notification)

            created_notifications.append(
                notification
            )



        db.commit()



        print(
            f"{len(created_notifications)} notifications created"
        )



        return created_notifications



    except Exception as e:


        db.rollback()



        print(
            "Bulk notification failed:"
        )

        print(str(e))



        return []



# =========================
# CREATE SIMPLE NOTIFICATION
# =========================

async def create_simple_notification(

    db,

    user_id: int,

    message: str
):

    return await create_system_notification(

        db=db,

        user_id=user_id,

        title="System Notification",

        message=message,

        notification_type="system"
    )