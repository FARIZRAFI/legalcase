from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from app.database import get_db

from app.models.timeline_model import TimelineEvent
from app.models.case_model import Case
from app.schemas.timeline_schema import TimelineCreate
from app.services.auth_service import verify_token

router = APIRouter(
    prefix="/timeline",
    tags=["Timeline"]
)

# =========================
# ADD TIMELINE EVENT
# =========================
@router.post("/", status_code=status.HTTP_201_CREATED)
def add_timeline_event(
    event: TimelineCreate,
    db: Session = Depends(get_db),
    user_data: dict = Depends(verify_token)
):
    case = db.query(Case).filter(Case.id == event.case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    timeline_event = TimelineEvent(
        case_id=event.case_id,
        title=event.title,
        description=event.description
    )
    db.add(timeline_event)
    db.commit()
    db.refresh(timeline_event)

    return {
        "message": "Timeline event added successfully",
        "timeline_id": timeline_event.id
    }

# =========================
# RECENT TIMELINE EVENTS (JOIN OPTIMIZED)
# =========================
@router.get("/recent/all")
def recent_timeline_events(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    user_data: dict = Depends(verify_token)
):
    events = (
        db.query(TimelineEvent)
        .options(joinedload(TimelineEvent.case))
        .order_by(TimelineEvent.created_at.desc(), TimelineEvent.id.desc())
        .limit(limit)
        .all()
    )

    formatted_events = [
        {
            "id": event.id,
            "case_id": event.case_id,
            "case_title": event.case.case_title if event.case else "Unknown Case",
            "title": event.title,
            "description": event.description,
            "created_at": event.created_at.isoformat() if event.created_at else None
        }
        for event in events
    ]

    return {
        "total": len(formatted_events),
        "events": formatted_events
    }

# =========================
# GET SINGLE TIMELINE EVENT
# =========================
@router.get("/event/{timeline_id}")
def get_single_timeline_event(
    timeline_id: int,
    db: Session = Depends(get_db),
    user_data: dict = Depends(verify_token)
):
    event = db.query(TimelineEvent).filter(TimelineEvent.id == timeline_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Timeline event not found")

    return {
        "id": event.id,
        "case_id": event.case_id,
        "title": event.title,
        "description": event.description,
        "created_at": event.created_at.isoformat() if event.created_at else None
    }

# =========================
# GET CASE TIMELINE (EXPLICIT SEGREGATED PATH)
# =========================
@router.get("/case/{case_id}")
def get_case_timeline(
    case_id: int,
    db: Session = Depends(get_db),
    user_data: dict = Depends(verify_token)
):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    events = (
        db.query(TimelineEvent)
        .filter(TimelineEvent.case_id == case_id)
        .order_by(TimelineEvent.created_at.desc(), TimelineEvent.id.desc())
        .all()
    )

    timeline = [
        {
            "id": event.id,
            "case_id": event.case_id,
            "title": event.title,
            "description": event.description,
            "created_at": event.created_at.isoformat() if event.created_at else None
        }
        for event in events
    ]

    return {
        "case_id": case.id,
        "case_title": case.case_title,
        "total_events": len(timeline),
        "timeline": timeline
    }

# =========================
# DELETE TIMELINE EVENT
# =========================
@router.delete("/{timeline_id}")
def delete_timeline_event(
    timeline_id: int,
    db: Session = Depends(get_db),
    user_data: dict = Depends(verify_token)
):
    timeline_event = db.query(TimelineEvent).filter(TimelineEvent.id == timeline_id).first()
    if not timeline_event:
        raise HTTPException(status_code=404, detail="Timeline event not found")

    db.delete(timeline_event)
    db.commit()
    return {"message": "Timeline event deleted successfully"}