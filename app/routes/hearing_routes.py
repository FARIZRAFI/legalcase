from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List

# Core system imports
from app.database import get_db
from app.models.hearing_model import Hearing
from app.models.case_model import Case
from app.models.user_model import User
from app.models.notification_model import Notification
from app.schemas.hearing_schema import HearingCreate
from app.routes.auth_routes import get_current_user_payload  # RESOLVES 401 UNAUTHORIZED
from app.services.whatsapp_service import send_whatsapp_message
from app.services.timeline_service import create_timeline_event

router = APIRouter(
    prefix="/hearings", 
    tags=["Hearings"]
)

# ==================================================
# GET ALL HEARINGS (FIXES THE 405 METHOD NOT ALLOWED)
# ==================================================
@router.get("")
@router.get("/")
def get_hearings(
    db: Session = Depends(get_db),
    user_data: dict = Depends(get_current_user_payload)
):
    """
    Fetches scheduled hearings dynamically based on user identity permissions.
    """
    role = user_data.get("role", "").lower()
    user_id = user_data.get("user_id")
    
    query = db.query(Hearing).join(Case)

    if role == "lawyer":
        query = query.filter(Case.lawyer_id == user_id)
    elif role == "client":
        query = query.filter(Case.client_id == user_id)
    # Admins bypass filters and view all system wide hearings

    return query.order_by(Hearing.hearing_date.asc()).all()


# =========================
# CREATE HEARING
# =========================
@router.post("", status_code=status.HTTP_201_CREATED)
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_hearing(
    hearing: HearingCreate, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db), 
    user_data: dict = Depends(get_current_user_payload)
):
    existing_case = db.query(Case).filter(Case.id == hearing.case_id).first()
    if not existing_case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Construct and save the hearing milestone
    new_hearing = Hearing(
    case_id=hearing.case_id,
    hearing_date=hearing.hearing_date,
    location=hearing.location,
    status=hearing.status,
    judge_name=hearing.judge_name,
    remarks=hearing.remarks
)
    db.add(new_hearing)
    db.commit()
    db.refresh(new_hearing)

    # 1. Update system logs and tracking history streams
    create_timeline_event(
        db=db, 
        case_id=existing_case.id, 
        title="Hearing Scheduled", 
        description=f"Date: {new_hearing.hearing_date}\nLocation: {new_hearing.location}"
    )
    
    # Inline database insertion avoids crashing from missing utility functions
    system_notification = Notification(
        user_id=user_data.get("user_id"),
        title="Hearing Scheduled",
        message=f"Case: {existing_case.case_title}",
        type="Hearing"
    )
    db.add(system_notification)
    db.commit()

    # 2. Safely offload background tasks to avoid locking requests
    client = db.query(User).filter(User.id == existing_case.client_id).first()
    if client and client.phone_number:
        message = (
            f"LEGAL HEARING SCHEDULED\n\n"
            f"Case: {existing_case.case_title}\n"
            f"Date: {new_hearing.hearing_date}\n"
            f"Location: {new_hearing.location}"
        )
        background_tasks.add_task(send_whatsapp_message, client.phone_number, message)

    return {
        "message": "Hearing scheduled successfully", 
        "hearing_id": new_hearing.id
    }


# =========================
# GET SINGLE HEARING
# =========================
@router.get("/{hearing_id}")
def get_hearing(
    hearing_id: int,
    db: Session = Depends(get_db),
    user_data: dict = Depends(get_current_user_payload)
):
    hearing = db.query(Hearing).filter(Hearing.id == hearing_id).first()
    if not hearing:
        raise HTTPException(status_code=404, detail="Hearing record not found")
    return hearing