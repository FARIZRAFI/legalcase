from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import SessionLocal

from app.models.case_model import Case
from app.models.hearing_model import Hearing
from app.models.notification_model import Notification

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dynamic Dashboard
@router.get("/dashboard")
def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):

    total_cases = db.query(Case).count()

    active_cases = db.query(Case).filter(
        Case.case_status == "Active"
    ).count()

    closed_cases = db.query(Case).filter(
        Case.case_status == "Closed"
    ).count()

    hearings = db.query(Hearing).count()

    notifications = db.query(Notification).count()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "total_cases": total_cases,
            "active_cases": active_cases,
            "closed_cases": closed_cases,
            "hearings": hearings,
            "notifications": notifications
        }
    )


# Dynamic Cases Page
@router.get("/cases")
def cases(
    request: Request,
    db: Session = Depends(get_db)
):

    cases_data = db.query(Case).all()

    return templates.TemplateResponse(
        request=request,
        name="cases.html",
        context={
            "cases": cases_data
        }
    )


# Dynamic Hearings Page
@router.get("/hearings")
def hearings(
    request: Request,
    db: Session = Depends(get_db)
):

    hearings_data = db.query(Hearing).all()

    return templates.TemplateResponse(
        request=request,
        name="hearings.html",
        context={
            "hearings": hearings_data
        }
    )