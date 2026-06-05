from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.hearing_model import Hearing
from app.models.case_model import Case
from app.models.user_model import User
from app.schemas.hearing_schema import HearingCreate
from app.services.auth_service import verify_token
from app.services.whatsapp_service import send_whatsapp_message
from app.services.notification_service import create_system_notification_sync
from app.services.timeline_service import create_timeline_event

router = APIRouter(prefix="/hearings", tags=["Hearings"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_hearing(hearing: HearingCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), user_data: dict = Depends(verify_token)):
    existing_case = db.query(Case).filter(Case.id == hearing.case_id).first()
    if not existing_case:
        raise HTTPException(status_code=404, detail="Case not found")

    new_hearing = Hearing(case_id=hearing.case_id, hearing_date=hearing.hearing_date, location=hearing.location, status=hearing.status)
    db.add(new_hearing)
    db.commit()
    db.refresh(new_hearing)

    # 1. Immediate Database Updates
    create_timeline_event(db=db, case_id=existing_case.id, title="Hearing Scheduled", description=f"Date: {new_hearing.hearing_date}\nLocation: {new_hearing.location}")
    create_system_notification_sync(db=db, user_id=user_data["user_id"], title="Hearing Scheduled", message=f"Case: {existing_case.case_title}", notification_type="Hearing")

    # 2. Offload the slow external network call to background workers
    client = db.query(User).filter(User.id == existing_case.client_id).first()
    if client and client.phone_number:
        message = f"LEGAL HEARING SCHEDULED\n\nCase: {existing_case.case_title}\nDate: {new_hearing.hearing_date}\nLocation: {new_hearing.location}"
        background_tasks.add_task(send_whatsapp_message, client.phone_number, message)

    return {"message": "Hearing scheduled successfully", "hearing_id": new_hearing.id}