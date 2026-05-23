from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from typing import Optional

from app.database import SessionLocal

from app.models.case_model import Case
from app.models.notification_model import Notification
from app.models.hearing_model import Hearing
from app.models.document_model import Document
from app.models.timeline_model import TimelineEvent

from app.schemas.case_schema import (
    CaseCreate,
    CaseUpdate
)

from app.services.auth_service import (
    verify_token
)

from app.services.timeline_service import (
    create_timeline_event
)


router = APIRouter(
    prefix="/cases",
    tags=["Cases"]
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
# CREATE CASE
# =========================

@router.post("/")
def create_case(

    case: CaseCreate,

    db: Session = Depends(get_db),

    user_data: dict = Depends(verify_token)
):

    new_case = Case(

        case_title=case.case_title,

        case_description=case.case_description,

        client_id=case.client_id,

        lawyer_id=case.lawyer_id,

        case_status="Open"
    )

    db.add(new_case)

    db.commit()

    db.refresh(new_case)



    # =========================
    # TIMELINE EVENT
    # =========================

    create_timeline_event(

        db=db,

        case_id=new_case.id,

        title="Case Created",

        description=f"""

Case:
{new_case.case_title}

Status:
{new_case.case_status}

Lawyer ID:
{new_case.lawyer_id}

Client ID:
{new_case.client_id}

        """
    )



    # =========================
    # NOTIFICATION
    # =========================

    notification = Notification(

        user_id=case.client_id,

        title="Case Created",

        message=f"New case created: {case.case_title}",

        type="case"
    )

    db.add(notification)

    db.commit()


    return {

        "message":
        "Case created successfully",

        "case_id":
        new_case.id
    }



# =========================
# GET ALL CASES
# =========================

@router.get("/")
def get_cases(

    skip: int = Query(0),

    limit: int = Query(100),

    db: Session = Depends(get_db),

    user_data: dict = Depends(verify_token)
):

    role = user_data.get("role")

    user_id = user_data.get("user_id")

    query = db.query(Case)


    # ADMIN
    if role == "admin":

        pass


    # LAWYER
    elif role == "lawyer":

        query = query.filter(
            Case.lawyer_id == user_id
        )


    # CLIENT
    elif role == "client":

        query = query.filter(
            Case.client_id == user_id
        )


    cases = query.order_by(
        Case.id.desc()
    ).offset(skip).limit(limit).all()

    return cases



# =========================
# GET SINGLE CASE
# =========================

@router.get("/{case_id}")
def get_case(

    case_id: int,

    db: Session = Depends(get_db),

    user_data: dict = Depends(verify_token)
):

    case = db.query(Case).filter(
        Case.id == case_id
    ).first()


    if not case:

        raise HTTPException(

            status_code=404,

            detail="Case not found"
        )


    return case



# =========================
# UPDATE CASE
# =========================

@router.put("/{case_id}")
def update_case(

    case_id: int,

    updated_case: CaseUpdate,

    db: Session = Depends(get_db),

    user_data: dict = Depends(verify_token)
):

    case = db.query(Case).filter(
        Case.id == case_id
    ).first()


    if not case:

        raise HTTPException(

            status_code=404,

            detail="Case not found"
        )


    if updated_case.case_title:

        case.case_title = updated_case.case_title


    if updated_case.case_description:

        case.case_description = updated_case.case_description


    if updated_case.case_status:

        case.case_status = updated_case.case_status


    if updated_case.lawyer_id:

        case.lawyer_id = updated_case.lawyer_id


    db.commit()

    db.refresh(case)



    # =========================
    # TIMELINE EVENT
    # =========================

    create_timeline_event(

        db=db,

        case_id=case.id,

        title="Case Updated",

        description=f"""

Case updated successfully.

Status:
{case.case_status}

Lawyer ID:
{case.lawyer_id}

        """
    )



    # =========================
    # LAWYER NOTIFICATION
    # =========================

    if updated_case.lawyer_id:

        lawyer_notification = Notification(

            user_id=updated_case.lawyer_id,

            title="Case Assigned",

            message=f"You have been assigned to case: {case.case_title}",

            type="case"
        )

        db.add(lawyer_notification)

        db.commit()



    # =========================
    # CLIENT NOTIFICATION
    # =========================

    notification = Notification(

        user_id=case.client_id,

        title="Case Updated",

        message=f"Case updated: {case.case_title}",

        type="case"
    )

    db.add(notification)

    db.commit()


    return {

        "message":
        "Case updated successfully"
    }



# =========================
# DELETE CASE
# =========================

@router.delete("/{case_id}")
def delete_case(

    case_id: int,

    db: Session = Depends(get_db),

    user_data: dict = Depends(verify_token)
):

    case = db.query(Case).filter(
        Case.id == case_id
    ).first()


    if not case:

        raise HTTPException(

            status_code=404,

            detail="Case not found"
        )



    # =========================
    # TIMELINE EVENT
    # =========================

    create_timeline_event(

        db=db,

        case_id=case.id,

        title="Case Deleted",

        description=f"""

Case deleted successfully.

Case:
{case.case_title}

        """
    )



    # DELETE RELATED HEARINGS
    db.query(Hearing).filter(
        Hearing.case_id == case_id
    ).delete()


    # DELETE RELATED DOCUMENTS
    db.query(Document).filter(
        Document.case_id == case_id
    ).delete()


    # DELETE RELATED TIMELINE EVENTS
    db.query(TimelineEvent).filter(
        TimelineEvent.case_id == case_id
    ).delete()


    # DELETE CASE
    db.delete(case)

    db.commit()


    return {

        "message":
        "Case deleted successfully"
    }



# =========================
# SEARCH CASES
# =========================

@router.get("/search/")
def search_cases(

    title: Optional[str] = None,

    status: Optional[str] = None,

    lawyer_id: Optional[int] = None,

    client_id: Optional[int] = None,

    db: Session = Depends(get_db),

    user_data: dict = Depends(verify_token)
):

    query = db.query(Case)


    if title:

        query = query.filter(
            Case.case_title.ilike(f"%{title}%")
        )


    if status:

        query = query.filter(
            Case.case_status == status
        )


    if lawyer_id:

        query = query.filter(
            Case.lawyer_id == lawyer_id
        )


    if client_id:

        query = query.filter(
            Case.client_id == client_id
        )


    return query.all()



# =========================
# ADVANCED SEARCH
# =========================

@router.get("/advanced-search/")
def advanced_search(

    query: str,

    db: Session = Depends(get_db),

    user_data: dict = Depends(verify_token)
):

    cases = db.query(Case).filter(

        or_(

            Case.case_title.ilike(f"%{query}%"),

            Case.case_description.ilike(f"%{query}%"),

            Case.case_status.ilike(f"%{query}%")
        )

    ).all()


    return cases