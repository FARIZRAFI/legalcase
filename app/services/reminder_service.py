from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from app.models.hearing_model import Hearing
from app.models.notification_model import Notification

def create_hearing_reminders(db: Session) -> dict:
    try:
        tomorrow_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        tomorrow_end = tomorrow_start + timedelta(hours=23, minutes=59, seconds=59)

        # Eager load the parent case relations
        hearings = (
            db.query(Hearing)
            .options(joinedload(Hearing.case))
            .filter(Hearing.hearing_date >= tomorrow_start, Hearing.hearing_date <= tomorrow_end, Hearing.status.in_(["Scheduled", "Upcoming"]))
            .all()
        )

        created_notifications = []

        for hearing in hearings:
            if not hearing.hearing_date or not hearing.case:
                continue

            existing_notification = (
                db.query(Notification)
                .filter(Notification.message.ilike(f"%case {hearing.case_id}%"), Notification.type == "hearing")
                .first()
            )

            if existing_notification:
                continue

            # Multi-user dynamic routing: Uses the actual client_id linked to the specific case
            notification = Notification(
                user_id=hearing.case.client_id,  
                title="Upcoming Hearing",
                message=f"Hearing for case {hearing.case_id} is scheduled tomorrow",
                type="hearing"
            )

            db.add(notification)
            created_notifications.append(notification)

        db.commit()
        return {"success": True, "message": "Hearing reminders processed", "count": len(created_notifications)}

    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}