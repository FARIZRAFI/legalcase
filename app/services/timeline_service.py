from sqlalchemy.orm import Session
from app.models.timeline_model import TimelineEvent

# =========================================================================
# AUDIT TRAIL TIMELINE MANAGEMENT SERVICES
# =========================================================================

def create_timeline_event(db: Session, case_id: int, title: str, description: str) -> TimelineEvent:
    """
    Creates a single database chronological milestone record. Includes 
    automatic transaction rollback protection schemas.
    """
    try:
        event = TimelineEvent(
            case_id=case_id,
            title=title,
            description=description
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        print(f"Timeline event created: {title}")
        return event
    except Exception as e:
        db.rollback()
        print(f"Timeline creation failed: {str(e)}")
        return None

def create_formatted_timeline_event(db: Session, case_id: int, title: str, lines: list) -> TimelineEvent:
    """
    Helper macro that accepts an array of strings, transforms them with inline 
    newline markers, and commits the output directly into the baseline pipeline.
    """
    description = "\n".join(lines)
    return create_timeline_event(
        db=db,
        case_id=case_id,
        title=title,
        description=description
    )

def delete_case_timeline(db: Session, case_id: int) -> bool:
    """
    Purges all timeline milestones associated with a specific legal file entry.
    """
    try:
        db.query(TimelineEvent).filter(TimelineEvent.case_id == case_id).delete()
        db.commit()
        print(f"Timeline deleted for case {case_id}")
        return True
    except Exception as e:
        db.rollback()
        print(f"Timeline delete failed: {str(e)}")
        return False

def get_case_timeline(db: Session, case_id: int) -> list:
    """
    Queries historical events for a specific case, sorting the resulting array 
    chronologically backwards from the most recent historical snapshot record.
    """
    try:
        return (
            db.query(TimelineEvent)
            .filter(TimelineEvent.case_id == case_id)
            .order_by(TimelineEvent.created_at.desc())
            .all()
        )
    except Exception as e:
        print(f"Timeline fetch failed: {str(e)}")
        return []