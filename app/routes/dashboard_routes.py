from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal

from app.models.case_model import Case
from app.models.hearing_model import Hearing
from app.models.notification_model import Notification
from app.models.document_model import Document

from app.services.auth_service import verify_token


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


# Database Dependency
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# Dashboard Analytics
@router.get("/")
def get_dashboard_data(
    db: Session = Depends(get_db),
    user_data: dict = Depends(verify_token)
):

    # Total Cases
    total_cases = db.query(Case).count()

    # Active Cases
    active_cases = db.query(Case).filter(
        Case.case_status == "Active"
    ).count()

    # Closed Cases
    closed_cases = db.query(Case).filter(
        Case.case_status == "Closed"
    ).count()

    # Total Hearings
    total_hearings = db.query(Hearing).count()

    # Upcoming Hearings
    upcoming_hearings = db.query(Hearing).filter(
        Hearing.status == "Upcoming"
    ).count()

    # Total Documents
    total_documents = db.query(Document).count()

    # Notifications for Logged-in User
    total_notifications = db.query(Notification).filter(
        Notification.user_id == user_data["user_id"]
    ).count()

    # Recent Cases
    recent_cases = db.query(Case).order_by(
        Case.id.desc()
    ).limit(5).all()

    # Recent Notifications
    recent_notifications = db.query(Notification).filter(
        Notification.user_id == user_data["user_id"]
    ).order_by(
        Notification.id.desc()
    ).limit(5).all()

    # Success Rate
    success_rate = 0

    if total_cases > 0:

        success_rate = (
            closed_cases / total_cases
        ) * 100

    return {

        "total_cases": total_cases,

        "active_cases": active_cases,

        "closed_cases": closed_cases,

        "total_hearings": total_hearings,

        "upcoming_hearings": upcoming_hearings,

        "notifications": total_notifications,

        "documents": total_documents,

        "success_rate": round(success_rate, 2),

        "recent_cases": [

            {
                "id": case.id,
                "title": case.case_title,
                "status": case.case_status
            }

            for case in recent_cases
        ],

        "recent_notifications": [

            {
                "id": notification.id,
                "message": notification.message,
                "type": notification.type
            }

            for notification in recent_notifications
        ]
    }