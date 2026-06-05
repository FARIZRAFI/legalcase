import os
from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

# Central system imports
from app.database import get_db
from app.models.case_model import Case
from app.models.hearing_model import Hearing
from app.models.notification_model import Notification
from app.models.document_model import Document
from app.models.timeline_model import TimelineEvent
from app.routes.auth_routes import get_current_user_payload  # Unified Auth Dependency

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


# =======================================================
# LENIENT AUTH HELPER FOR WEB PAGES (Graces Redirection)
# =======================================================
async def get_page_user_or_none(request: Request) -> os.getenv:
    """
    Reads authentication tokens from browser cookies. If the user session
    is missing or expired, returns None instead of throwing a rigid 401 JSON error.
    """
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        # Strip Bearer prefix if appended by browser client storage mechanisms
        if token.startswith("Bearer "):
            token = token.split(" ")[1]
        
        from jose import jwt
        from app.services.auth_service import SECRET_KEY, ALGORITHM
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        return None


# =========================
# LOGIN PAGE
# =========================
@router.get("")
@router.get("/")
async def login_page(request: Request, user_data: dict = Depends(get_page_user_or_none)):
    # If user is already authenticated, bypass login and skip straight to dashboard
    if user_data:
        return RedirectResponse(url="/dashboard-page", status_code=status.HTTP_302_FOUND)
        
    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )


# =======================================================
# CORE APPLICATION PAGES (Supports both -page and -view)
# =======================================================

@router.get("/dashboard-page")
@router.get("/dashboard-view")
async def dashboard_page(request: Request, user_data: dict = Depends(get_page_user_or_none)):
    if not user_data:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(request=request, name="dashboard.html")


@router.get("/cases-page")
@router.get("/cases-view")
async def cases_page(request: Request, user_data: dict = Depends(get_page_user_or_none)):
    if not user_data:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(request=request, name="cases.html")


@router.get("/hearings-page")
@router.get("/hearings-view")
async def hearings_page(request: Request, user_data: dict = Depends(get_page_user_or_none)):
    if not user_data:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(request=request, name="hearings.html")


@router.get("/notifications-page")
@router.get("/notifications-view")
async def notifications_page(request: Request, user_data: dict = Depends(get_page_user_or_none)):
    if not user_data:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(request=request, name="notifications.html")


@router.get("/timeline-page")
@router.get("/timeline-view")
async def timeline_page(request: Request, user_data: dict = Depends(get_page_user_or_none)):
    if not user_data:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(request=request, name="timeline.html")


@router.get("/documents-page")
@router.get("/documents-view")
async def documents_page(request: Request, user_data: dict = Depends(get_page_user_or_none)):
    if not user_data:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(request=request, name="documents.html")


# =======================================================
# DASHBOARD API ENDPOINTS (FIXES THE 404 NOT FOUND ERRORS)
# =======================================================

@router.get("/dashboard/summary")
@router.get("/dashboard-stats")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    user_data: dict = Depends(get_current_user_payload)
):
    """
    Returns data metric summaries. Leverages role scopes to isolate views 
    for lawyers, clients, and administrators.
    """
    role = user_data.get("role", "").lower()
    user_id = user_data.get("user_id")

    # Base query sets
    case_query = db.query(Case)
    hearing_query = db.query(Hearing).join(Case)
    document_query = db.query(Document).join(Case)

    # Apply tenancy matrix logic rules
    if role == "lawyer":
        case_query = case_query.filter(Case.lawyer_id == user_id)
        hearing_query = hearing_query.filter(Case.lawyer_id == user_id)
        document_query = document_query.filter(Case.lawyer_id == user_id)
    elif role == "client":
        case_query = case_query.filter(Case.client_id == user_id)
        hearing_query = hearing_query.filter(Case.client_id == user_id)
        document_query = document_query.filter(Case.client_id == user_id)

    total_cases = case_query.count()
    active_cases = case_query.filter(Case.case_status == "Active").count()
    closed_cases = case_query.filter(Case.case_status == "Closed").count()
    
    return {
        "total_cases": total_cases,
        "active_cases": active_cases,
        "closed_cases": closed_cases,
        "total_hearings": hearing_query.count(),
        "total_documents": document_query.count(),
        "total_notifications": db.query(Notification).filter(Notification.user_id == user_id).count()
    }


@router.get("/dashboard/recent-feed")
def get_dashboard_recent_feed(
    db: Session = Depends(get_db),
    user_data: dict = Depends(get_current_user_payload)
):
    """
    Fetches the 5 most recent timeline developments across all valid operational scopes.
    """
    role = user_data.get("role", "").lower()
    user_id = user_data.get("user_id")

    query = db.query(TimelineEvent).options(joinedload(TimelineEvent.case)).join(Case)

    if role == "lawyer":
        query = query.filter(Case.lawyer_id == user_id)
    elif role == "client":
        query = query.filter(Case.client_id == user_id)

    events = query.order_by(TimelineEvent.created_at.desc(), TimelineEvent.id.desc()).limit(5).all()

    return [{
        "id": event.id,
        "case_title": event.case.case_title if event.case else "System Log",
        "title": event.title,
        "description": event.description,
        "created_at": event.created_at.isoformat() if event.created_at else None
    } for event in events]


# =========================
# HEALTH CHECK
# =========================
@router.get("/page-health")
def page_health():
    return {
        "status": "healthy",
        "message": "Template UI render layer working successfully"
    }