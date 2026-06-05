from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.database import get_db

from app.models.case_model import Case
from app.models.hearing_model import Hearing
from app.models.document_model import Document
from app.models.timeline_model import TimelineEvent
from app.services.auth_service import verify_token

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard Analytics"]
)

# =========================================================================
# DETAILED ANALYTICS AGGREGATION ENGINE
# Compiles structured statistical distributions for frontend charts
# =========================================================================
@router.get("/summary")
def get_dashboard_extended_summary(
    db: Session = Depends(get_db),
    user_data: dict = Depends(verify_token)
):
    """
    Assembles a unified metadata response containing status splits, system totals,
    and a weekly event volume timeline used to render dashboard metrics.
    """
    try:
        # 1. Total KPI Metrics Counts
        total_cases = db.query(Case).count()
        total_hearings = db.query(Hearing).count()
        total_documents = db.query(Document).count()

        # 2. Case Status Percentage Distribution Splits
        active_count = db.query(Case).filter(Case.case_status == "Active").count()
        closed_count = db.query(Case).filter(Case.case_status == "Closed").count()
        pending_count = db.query(Case).filter(Case.case_status == "Pending").count()

        # 3. Time-Series Aggregation: Activity volume over the last 7 days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        timeline_activity = (
            db.query(
                func.to_char(TimelineEvent.created_at, 'YYYY-MM-DD').label('date'),
                func.count(TimelineEvent.id).label('count')
            )
            .filter(TimelineEvent.created_at >= seven_days_ago)
            .group_by('date')
            .order_by('date')
            .all()
        )

        # Structure time-series list cleanly for chart data targets
        activity_trends = [{"date": row.date, "events": row.count} for row in timeline_activity]

        return {
            "counters": {
                "total_cases": total_cases,
                "total_hearings": total_hearings,
                "total_documents": total_documents
            },
            "status_distribution": {
                "active": active_count,
                "closed": closed_count,
                "pending": pending_count,
                "ratios": {
                    "active_percent": round((active_count / total_cases * 100), 2) if total_cases > 0 else 0,
                    "closed_percent": round((closed_count / total_cases * 100), 2) if total_cases > 0 else 0,
                    "pending_percent": round((pending_count / total_cases * 100), 2) if total_cases > 0 else 0,
                }
            },
            "activity_trends": activity_trends
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate analytics overview metrics: {str(e)}"
        )

# =========================================================================
# LATEST WORKSPACE FEEDS (JOIN FREE)
# Pulls the 5 most critical high-priority contextual updates for the user feed
# =========================================================================
@router.get("/recent-feed")
def get_dashboard_recent_feed(
    limit: int = 5,
    db: Session = Depends(get_db),
    user_data: dict = Depends(verify_token)
):
    """
    Returns an activity feed snapshot of the newest historical events 
    across the legal workspace framework.
    """
    recent_events = (
        db.query(TimelineEvent)
        .order_by(TimelineEvent.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": event.id,
            "case_id": event.case_id,
            "title": event.title,
            "description": event.description,
            "timestamp": event.created_at.isoformat() if event.created_at else None
        }
        for event in recent_events
    ]