from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session
from sqlalchemy import extract

from datetime import datetime

from app.database import SessionLocal

from app.models.hearing_model import Hearing
from app.models.case_model import Case
from app.models.user_model import User

from app.schemas.hearing_schema import (
    HearingCreate
)

from app.services.auth_service import (
    verify_token
)

from app.services.whatsapp_service import (
    send_whatsapp_message
)

from app.services.notification_service import (
    create_system_notification
)

from app.services.timeline_service import (
    create_timeline_event
)


router = APIRouter(
    prefix="/hearings",
    tags=["Hearings"]
)



# =========================
# DATABASE CONNECTION
# =========================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()



# =========================
# CREATE HEARING
# =========================

@router.post("/")
async def create_hearing(

    hearing: HearingCreate,

    db: Session = Depends(get_db),

    user_data: dict = Depends(verify_token)

):

    existing_case = db.query(Case).filter(
        Case.id == hearing.case_id
    ).first()


    if not existing_case:

        raise HTTPException(

            status_code=404,

            detail="Case not found"
        )


    new_hearing = Hearing(

        case_id=hearing.case_id,

        hearing_date=hearing.hearing_date,

        location=hearing.location,

        status=hearing.status
    )

    db.add(new_hearing)

    db.commit()

    db.refresh(new_hearing)



    # =========================
    # TIMELINE EVENT
    # =========================

    create_timeline_event(

        db=db,

        case_id=existing_case.id,

        title="Hearing Scheduled",

        description=f"""

Date:
{new_hearing.hearing_date}

Location:
{new_hearing.location}

Status:
{new_hearing.status}

        """
    )



    # =========================
    # CREATE NOTIFICATION
    # =========================

    await create_system_notification(

        db=db,

        user_id=user_data["user_id"],

        title="Hearing Scheduled",

        message=f"""

Case:
{existing_case.case_title}

Date:
{new_hearing.hearing_date}

Location:
{new_hearing.location}

        """,

        notification_type="Hearing"
    )



    # =========================
    # SEND WHATSAPP
    # =========================

    client = db.query(User).filter(
        User.id == existing_case.client_id
    ).first()


    if client and client.phone_number:

        message = f"""
LEGAL HEARING SCHEDULED

Case:
{existing_case.case_title}

Date:
{new_hearing.hearing_date}

Location:
{new_hearing.location}

Status:
{new_hearing.status}
"""

        try:

            send_whatsapp_message(
                client.phone_number,
                message
            )

            print(
                "WHATSAPP SENT"
            )

        except Exception as e:

            print(
                "WHATSAPP ERROR:",
                e
            )



    return {

        "message":
        "Hearing scheduled successfully",

        "hearing_id":
        new_hearing.id
    }



# =========================
# UPDATE HEARING
# =========================

@router.put("/{hearing_id}")
async def update_hearing(

    hearing_id: int,

    updated_data: HearingCreate,

    db: Session = Depends(get_db),

    user_data: dict = Depends(verify_token)

):

    hearing = db.query(Hearing).filter(
        Hearing.id == hearing_id
    ).first()


    if not hearing:

        raise HTTPException(

            status_code=404,

            detail="Hearing not found"
        )


    existing_case = db.query(Case).filter(
        Case.id == updated_data.case_id
    ).first()


    if not existing_case:

        raise HTTPException(

            status_code=404,

            detail="Case not found"
        )


    old_date = hearing.hearing_date


    hearing.case_id = updated_data.case_id

    hearing.hearing_date = updated_data.hearing_date

    hearing.location = updated_data.location

    hearing.status = updated_data.status

    db.commit()

    db.refresh(hearing)



    # =========================
    # TIMELINE EVENT
    # =========================

    create_timeline_event(

        db=db,

        case_id=existing_case.id,

        title="Hearing Updated",

        description=f"""

Old Date:
{old_date}

New Date:
{hearing.hearing_date}

Location:
{hearing.location}

Status:
{hearing.status}

        """
    )



    # =========================
    # CREATE NOTIFICATION
    # =========================

    await create_system_notification(

        db=db,

        user_id=user_data["user_id"],

        title="Hearing Rescheduled",

        message=f"""

Case:
{existing_case.case_title}

Old Date:
{old_date}

New Date:
{hearing.hearing_date}

Location:
{hearing.location}

        """,

        notification_type="Reschedule"
    )



    # =========================
    # SEND WHATSAPP
    # =========================

    client = db.query(User).filter(
        User.id == existing_case.client_id
    ).first()


    if client and client.phone_number:

        message = f"""
LEGAL HEARING UPDATED

Case:
{existing_case.case_title}

Old Date:
{old_date}

New Date:
{hearing.hearing_date}

Location:
{hearing.location}

Status:
{hearing.status}
"""

        try:

            send_whatsapp_message(
                client.phone_number,
                message
            )

            print(
                "WHATSAPP UPDATE SENT"
            )

        except Exception as e:

            print(
                "WHATSAPP UPDATE ERROR:",
                e
            )



    return {

        "message":
        "Hearing updated successfully"
    }



# =========================
# DELETE HEARING
# =========================

@router.delete("/{hearing_id}")
async def delete_hearing(

    hearing_id: int,

    db: Session = Depends(get_db),

    user_data: dict = Depends(verify_token)

):

    hearing = db.query(Hearing).filter(
        Hearing.id == hearing_id
    ).first()


    if not hearing:

        raise HTTPException(

            status_code=404,

            detail="Hearing not found"
        )


    hearing_location = hearing.location

    hearing_case_id = hearing.case_id

    hearing_db_id = hearing.id



    # =========================
    # TIMELINE EVENT
    # =========================

    create_timeline_event(

        db=db,

        case_id=hearing_case_id,

        title="Hearing Deleted",

        description=f"""

Location:
{hearing_location}

Hearing removed successfully.

        """
    )



    # =========================
    # NOTIFICATION
    # =========================

    await create_system_notification(

        db=db,

        user_id=user_data["user_id"],

        title="Hearing Deleted",

        message=f"""

Hearing ID:
{hearing_db_id}

Location:
{hearing_location}

        """,

        notification_type="Delete"
    )



    db.delete(hearing)

    db.commit()



    return {

        "message":
        "Hearing deleted successfully"
    }



# =========================
# GET ALL HEARINGS
# =========================

@router.get("/")
def get_hearings(

    db: Session = Depends(get_db),

    user_data: dict = Depends(verify_token)

):

    hearings = db.query(Hearing).order_by(

        Hearing.hearing_date.desc()

    ).all()


    results = []


    for hearing in hearings:

        case = db.query(Case).filter(
            Case.id == hearing.case_id
        ).first()


        title = f"Case #{hearing.case_id}"

        if case:

            title = case.case_title


        results.append({

            "id":
            hearing.id,

            "title":
            title,

            "case_id":
            hearing.case_id,

            "hearing_date":
            hearing.hearing_date.isoformat()
            if hearing.hearing_date
            else None,

            "location":
            hearing.location,

            "status":
            hearing.status
        })


    return results



# =========================
# UPCOMING HEARINGS
# =========================

@router.get("/upcoming")
def upcoming_hearings(

    limit: int = 10,

    db: Session = Depends(get_db),

    user_data: dict = Depends(verify_token)

):

    hearings = db.query(Hearing).filter(

        Hearing.hearing_date >= datetime.utcnow()

    ).order_by(

        Hearing.hearing_date.asc()

    ).limit(limit).all()


    results = []


    for hearing in hearings:

        case = db.query(Case).filter(
            Case.id == hearing.case_id
        ).first()


        title = f"Case #{hearing.case_id}"

        if case:

            title = case.case_title


        results.append({

            "id":
            hearing.id,

            "title":
            title,

            "case_id":
            hearing.case_id,

            "hearing_date":
            hearing.hearing_date.isoformat()
            if hearing.hearing_date
            else None,

            "location":
            hearing.location,

            "status":
            hearing.status
        })


    return results



# =========================
# CALENDAR EVENTS
# =========================

@router.get("/calendar")
def hearing_calendar(

    month: int,

    year: int,

    db: Session = Depends(get_db),

    user_data: dict = Depends(verify_token)

):

    hearings = db.query(Hearing).filter(

        extract(
            "month",
            Hearing.hearing_date
        ) == month,

        extract(
            "year",
            Hearing.hearing_date
        ) == year

    ).all()


    events = []


    for hearing in hearings:

        case = db.query(Case).filter(
            Case.id == hearing.case_id
        ).first()


        title = f"Case #{hearing.case_id}"

        if case:

            title = case.case_title


        events.append({

            "id":
            hearing.id,

            "title":
            title,

            "start":
            hearing.hearing_date.isoformat()
            if hearing.hearing_date
            else None,

            "extendedProps": {

                "location":
                hearing.location,

                "status":
                hearing.status,

                "case_id":
                hearing.case_id
            }
        })


    return events