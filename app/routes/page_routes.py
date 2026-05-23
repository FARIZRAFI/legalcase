from fastapi import (
    APIRouter,
    Request
)

from fastapi.responses import (
    HTMLResponse
)

from fastapi.templating import (
    Jinja2Templates
)


router = APIRouter()


templates = Jinja2Templates(
    directory="app/templates"
)



# =========================
# LOGIN PAGE
# =========================

@router.get(
    "/",
    response_class=HTMLResponse
)
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

@router.get(
    "/dashboard-page",
    response_class=HTMLResponse
)
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

@router.get(
    "/cases-page",
    response_class=HTMLResponse
)
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

@router.get(
    "/hearings-page",
    response_class=HTMLResponse
)
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

@router.get(
    "/notifications-page",
    response_class=HTMLResponse
)
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

@router.get(
    "/timeline-page",
    response_class=HTMLResponse
)
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

@router.get(
    "/documents-page",
    response_class=HTMLResponse
)
async def documents_page(

    request: Request
):

    return templates.TemplateResponse(

        request=request,

        name="documents.html"
    )



# =========================
# PAGE HEALTH CHECK
# =========================

@router.get("/page-health")
async def page_health():

    return {

        "status":
        "healthy",

        "message":
        "Page routes working successfully"
    }