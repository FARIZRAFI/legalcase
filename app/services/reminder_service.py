from datetime import (
    datetime,
    timedelta
)

from sqlalchemy.orm import Session

from app.models.hearing_model import (
    Hearing
)

from app.models.notification_model import (
    Notification
)



# =========================
# CREATE HEARING REMINDERS
# =========================

def create_hearing_reminders(
    db: Session
):

    try:


        # TOMORROW DATE
        tomorrow = (

            datetime.utcnow() +

            timedelta(days=1)
        ).date()



        # GET HEARINGS
        hearings = db.query(
            Hearing
        ).all()



        created_notifications = []



        for hearing in hearings:


            # SAFE DATE CHECK
            if not hearing.hearing_date:

                continue



            # ONLY UPCOMING
            if hearing.status not in [

                "Scheduled",

                "Upcoming"
            ]:

                continue



            hearing_date = (
                hearing.hearing_date.date()
            )



            # CHECK TOMORROW
            if hearing_date == tomorrow:



                # PREVENT DUPLICATE REMINDERS
                existing_notification = db.query(
                    Notification
                ).filter(

                    Notification.message.ilike(
                        f"%case {hearing.case_id}%"
                    ),

                    Notification.type == "hearing"
                ).first()



                if existing_notification:

                    continue



                # CREATE NOTIFICATION
                notification = Notification(

                    user_id=1,

                    title="Upcoming Hearing",

                    message=(
                        f"Hearing for case "
                        f"{hearing.case_id} "
                        f"is scheduled tomorrow"
                    ),

                    type="hearing"
                )



                db.add(notification)

                created_notifications.append(
                    notification
                )



        db.commit()



        print(
            f"{len(created_notifications)} hearing reminders created"
        )



        return {

            "success":
            True,

            "message":
            "Hearing reminders created successfully",

            "count":
            len(created_notifications)
        }



    except Exception as e:


        db.rollback()



        print(
            "Reminder creation failed:"
        )

        print(str(e))



        return {

            "success":
            False,

            "error":
            str(e)
        }