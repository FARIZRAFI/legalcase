from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db

from app.models.case_model import Case
from app.models.hearing_model import Hearing
from app.models.notification_model import Notification
from app.models.document_model import Document
from app.models.timeline_model import TimelineEvent

router = APIRouter(
    tags=["UI View Engine"]
)

templates = Jinja2Templates(directory="app/templates")

# Cookie authentication parser for server-side HTML rendering
async def verify_ui_authentication(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        if token.startswith("Bearer "):
            token = token.split(" ")[1]
        from app.services.auth_service import verify_token
        return verify_token(token)
    except Exception:
        return None

@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request, user_data: dict = Depends(verify_ui_authentication)):
    if user_data:
        return RedirectResponse(url="/dashboard-page", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/dashboard-page", response_class=HTMLResponse)
async def dashboard_page(request: Request, user_data: dict = Depends(verify_ui_authentication)):
    if not user_data:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user_data})

@router.get("/cases-page", response_class=HTMLResponse)
async def cases_page(request: Request, user_data: dict = Depends(verify_ui_authentication)):
    if not user_data:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("cases.html", {"request": request, "user": user_data})

@router.get("/hearings-page", response_class=HTMLResponse)
async def hearings_page(request: Request, user_data: dict = Depends(verify_ui_authentication)):
    if not user_data:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("hearings.html", {"request": request, "user": user_data})

@router.get("/notifications-page", response_class=HTMLResponse)
async def notifications_page(request: Request, user_data: dict = Depends(verify_ui_authentication)):
    if not user_data:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("notifications.html", {"request": request, "user": user_data})

@router.get("/timeline-page", response_class=HTMLResponse)
async def timeline_page(request: Request, user_data: dict = Depends(verify_ui_authentication)):
    if not user_data:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("timeline.html", {"request": request, "user": user_data})

@router.get("/documents-page", response_class=HTMLResponse)
async def documents_page(request: Request, user_data: dict = Depends(verify_ui_authentication)):
    if not user_data:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("documents.html", {"request": request, "user": user_data})

@router.get("/dashboard-stats")
def dashboard_stats(db: Session = Depends(get_db), user_data: dict = Depends(verify_ui_authentication)):
    if not user_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session context expired")
    return {
        "total_cases": db.query(Case).count(),
        "active_cases": db.query(Case).filter(Case.case_status == "Active").count(),
        "closed_cases": db.query(Case).filter(Case.case_status == "Closed").count(),
        "total_hearings": db.query(Hearing).count(),
        "total_notifications": db.query(Notification).count(),
        "total_documents": db.query(Document).count(),
        "total_timeline_events": db.query(TimelineEvent).count()
    }

@router.get("/page-health")
def page_health():
    return {"status": "healthy", "message": "UI systems normal"}