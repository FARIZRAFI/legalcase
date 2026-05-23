from fastapi import (
    APIRouter,
    Request,
    Depends
)

from fastapi.responses import (
    RedirectResponse
)

from fastapi.templating import (
    Jinja2Templates
)

from sqlalchemy.orm import Session

from app.database import SessionLocal

from app.models.case_model import (
    Case
)

from app.models.hearing_model import (
    Hearing
)

from app.models.notification_model import (
    Notification
)

from app.models.document_model import (
    Document
)

from app.models.timeline_model import (
    TimelineEvent
)

from app.services.auth_service import (
    verify_token
)


router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
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
# LOGIN PAGE
# =========================

@router.get("/")
async def login_page(
    request: Request
):

    return templates.TemplateResponse(

        request=request,

        name="login.html"
    )



# =========================
# DASHBOARD PAGE
# =========================

@router.get("/dashboard-page")
async def dashboard_page(

    request: Request
):

    return templates.TemplateResponse(

        request=request,

        name="dashboard.html"
    )



# =========================
# CASES PAGE
# =========================

@router.get("/cases-page")
async def cases_page(

    request: Request
):

    return templates.TemplateResponse(

        request=request,

        name="cases.html"
    )



# =========================
# HEARINGS PAGE
# =========================

@router.get("/hearings-page")
async def hearings_page(

    request: Request
):

    return templates.TemplateResponse(

        request=request,

        name="hearings.html"
    )



# =========================
# NOTIFICATIONS PAGE
# =========================

@router.get("/notifications-page")
async def notifications_page(

    request: Request
):

    return templates.TemplateResponse(

        request=request,

        name="notifications.html"
    )



# =========================
# TIMELINE PAGE
# =========================

@router.get("/timeline-page")
async def timeline_page(

    request: Request
):

    return templates.TemplateResponse(

        request=request,

        name="timeline.html"
    )



# =========================
# DOCUMENTS PAGE
# =========================

@router.get("/documents-page")
async def documents_page(

    request: Request
):

    return templates.TemplateResponse(

        request=request,

        name="documents.html"
    )



# =========================
# DYNAMIC DASHBOARD STATS
# =========================

@router.get("/dashboard-stats")
def dashboard_stats(

    db: Session = Depends(get_db)
):

    total_cases = db.query(
        Case
    ).count()


    active_cases = db.query(
        Case
    ).filter(

        Case.case_status == "Active"

    ).count()


    closed_cases = db.query(
        Case
    ).filter(

        Case.case_status == "Closed"

    ).count()


    total_hearings = db.query(
        Hearing
    ).count()


    total_notifications = db.query(
        Notification
    ).count()


    total_documents = db.query(
        Document
    ).count()


    total_timeline_events = db.query(
        TimelineEvent
    ).count()



    return {

        "total_cases":
        total_cases,

        "active_cases":
        active_cases,

        "closed_cases":
        closed_cases,

        "total_hearings":
        total_hearings,

        "total_notifications":
        total_notifications,

        "total_documents":
        total_documents,

        "total_timeline_events":
        total_timeline_events
    }



# =========================
# HEALTH CHECK
# =========================

@router.get("/page-health")
def page_health():

    return {

        "status":
        "healthy",

        "message":
        "Page routes working successfully"
    }