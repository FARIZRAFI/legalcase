from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.hearing_model import Hearing
from app.models.notification_model import Notification


def create_hearing_reminders(db: Session):

    tomorrow = datetime.utcnow() + timedelta(days=1)

    hearings = db.query(Hearing).all()

    created_notifications = []

    for hearing in hearings:

        hearing_date = hearing.hearing_date

        # Check if hearing is tomorrow
        if hearing_date.date() == tomorrow.date():

            notification = Notification(

                user_id=1,

                title="Upcoming Hearing",

                message=f"Hearing for case {hearing.case_id} is tomorrow",

                type="hearing"

            )

            db.add(notification)

            created_notifications.append(notification)

    db.commit()

    return {
        "message": "Hearing reminders created",
        "count": len(created_notifications)
    }