from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional

# Import global database and auth engines cleanly
from app.database import get_db
from app.models.case_model import Case
from app.models.notification_model import Notification
from app.models.hearing_model import Hearing
from app.models.document_model import Document
from app.models.timeline_model import TimelineEvent
from app.schemas.case_schema import CaseCreate, CaseUpdate
from app.routes.auth_routes import get_current_user_payload  # RESOLVES 401 UNAUTHORIZED
from app.services.timeline_service import create_timeline_event

router = APIRouter(
    prefix="/cases",
    tags=["Cases"]
)


# ==================================================
# SEARCH ROUTES (Placed first to avoid route conflict)
# ==================================================

@router.get("/search")
@router.get("/search/")
def search_cases(
    title: Optional[str] = None,
    status: Optional[str] = None,
    lawyer_id: Optional[int] = None,
    client_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user_data: dict = Depends(get_current_user_payload)
):
    query = db.query(Case)

    if title:
        query = query.filter(Case.case_title.ilike(f"%{title}%"))
    if status:
        query = query.filter(Case.case_status == status)
    if lawyer_id:
        query = query.filter(Case.lawyer_id == lawyer_id)
    if client_id:
        query = query.filter(Case.client_id == client_id)

    return query.order_by(Case.id.desc()).all()


@router.get("/advanced-search")
@router.get("/advanced-search/")
def advanced_search(
    query: str,
    db: Session = Depends(get_db),
    user_data: dict = Depends(get_current_user_payload)
):
    cases = db.query(Case).filter(
        or_(
            Case.case_title.ilike(f"%{query}%"),
            Case.case_description.ilike(f"%{query}%"),
            Case.case_status.ilike(f"%{query}%")
        )
    ).order_by(Case.id.desc()).all()
    
    return cases


# =========================
# CREATE CASE
# =========================

@router.post("")
@router.post("/")
def create_case(
    case: CaseCreate,
    db: Session = Depends(get_db),
    user_data: dict = Depends(get_current_user_payload)
):
    # 1. Resolve target lawyer ID safely
    assigned_lawyer_id = case.lawyer_id
    if not assigned_lawyer_id and user_data.get("role", "").lower() == "lawyer":
        assigned_lawyer_id = user_data.get("user_id")

    # 2. Build model object ensuring all constraints map fully
    new_case = Case(
        case_number=case.case_number,                     # Fixed: Added missing mapping
        case_title=case.case_title,
        case_description=case.case_description or "",    # Fixed: Fallback empty string avoids database Null crash
        client_id=case.client_id,
        lawyer_id=assigned_lawyer_id,                    # Fixed: Uses resolved safe ID reference
        case_status=case.case_status or "Open"
    )
    
    try:
        db.add(new_case)
        db.commit()
        db.refresh(new_case)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database insertion failed. Verify unique case_number constraints. Error: {str(e)}"
        )

    # 3. Log milestone timeline capture safely
    try:
        create_timeline_event(
            db=db,
            case_id=new_case.id,
            title="Case Created",
            description=f"Case Number: {new_case.case_number}\nTitle: {new_case.case_title}\nStatus: {new_case.case_status}"
        )
    except Exception as timeline_err:
        print(f"[Warning] Case saved, but timeline event generation skipped: {str(timeline_err)}")

    # 4. Send dynamic transactional in-app notification context safely
    try:
        notification = Notification(
            user_id=case.client_id,
            title="Case Created",
            message=f"New case created: {case.case_title} (Ref: {case.case_number})",
            type="case"
        )
        db.add(notification)
        db.commit()
    except Exception as notification_err:
        db.rollback()
        print(f"[Warning] Case saved, but client push notification skipped: {str(notification_err)}")

    return {
        "message": "Case created successfully",
        "case_id": new_case.id
    }

# =========================
# GET ALL CASES
# =========================

@router.get("")
@router.get("/")
def get_cases(
    skip: int = Query(0),
    limit: int = Query(100),
    db: Session = Depends(get_db),
    user_data: dict = Depends(get_current_user_payload)
):
    role = user_data.get("role", "").lower()
    user_id = user_data.get("user_id")
    query = db.query(Case)

    # Multi-tenant operational workspace filtering criteria rules
    if role == "lawyer":
        query = query.filter(Case.lawyer_id == user_id)
    elif role == "client":
        query = query.filter(Case.client_id == user_id)
    # Admin role skips filters and views all elements

    return query.order_by(Case.id.desc()).offset(skip).limit(limit).all()


# =========================
# GET SINGLE CASE
# =========================

@router.get("/{case_id}")
def get_case(
    case_id: int,
    db: Session = Depends(get_db),
    user_data: dict = Depends(get_current_user_payload)
):
    case = db.query(Case).filter(Case.id == case_id).first()
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
    user_data: dict = Depends(get_current_user_payload)
):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found"
        )

    # Apply partial delta mutations 
    if updated_case.case_title is not None:
        case.case_title = updated_case.case_title
    if updated_case.case_description is not None:
        case.case_description = updated_case.case_description
    if updated_case.case_status is not None:
        case.case_status = updated_case.case_status
    if updated_case.lawyer_id is not None:
        case.lawyer_id = updated_case.lawyer_id

    db.commit()
    db.refresh(case)

    # Log structural shift to target historical timeline track
    create_timeline_event(
        db=db,
        case_id=case.id,
        title="Case Updated",
        description=f"Case updated successfully.\n\nStatus:\n{case.case_status}\n\nLawyer ID:\n{case.lawyer_id}"
    )

    # Alert legal counsel if re-assigned
    if updated_case.lawyer_id is not None:
        lawyer_notification = Notification(
            user_id=updated_case.lawyer_id,
            title="Case Assigned",
            message=f"You have been assigned to case: {case.case_title}",
            type="case"
        )
        db.add(lawyer_notification)

    # Alert the client
    client_notification = Notification(
        user_id=case.client_id,
        title="Case Updated",
        message=f"Case updated: {case.case_title}",
        type="case"
    )
    db.add(client_notification)
    
    db.commit()

    return {"message": "Case updated successfully"}


# =========================
# DELETE CASE
# =========================

@router.delete("/{case_id}")
def delete_case(
    case_id: int,
    db: Session = Depends(get_db),
    user_data: dict = Depends(get_current_user_payload)
):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found"
        )

    case_title = case.case_title

    # Cascading safe database foreign target deletes manually
    db.query(Hearing).filter(Hearing.case_id == case_id).delete()
    db.query(Document).filter(Document.case_id == case_id).delete()
    db.query(Notification).filter(Notification.user_id == case.client_id).delete()
    db.query(TimelineEvent).filter(TimelineEvent.case_id == case_id).delete()

    db.delete(case)
    db.commit()

    return {"message": f"Case '{case_title}' deleted successfully"}