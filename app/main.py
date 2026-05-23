import os
import uvicorn

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles

from app.database import engine, Base

# Import Models
from app.models.user_model import User
from app.models.case_model import Case
from app.models.timeline_model import TimelineEvent
from app.models.hearing_model import Hearing
from app.models.notification_model import Notification
from app.models.document_model import Document

# Import Routers
from app.routes.auth_routes import router as auth_router
from app.routes.case_routes import router as case_router
from app.routes.timeline_routes import router as timeline_router
from app.routes.hearing_routes import router as hearing_router
from app.routes.notification_routes import (
    router as notification_router
)
from app.routes.document_routes import (
    router as document_router
)
from app.routes.dashboard_routes import (
    router as dashboard_router
)
from app.routes.websocket_routes import (
    router as websocket_router
)
from app.routes.page_routes import (
    router as page_router
)

from app.services.auth_service import verify_token

# Create Database Tables
Base.metadata.create_all(bind=engine)

# Create FastAPI App
app = FastAPI(
    title="Legal Case Management System"
)

# =========================
# STATIC FILES FIX
# =========================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

STATIC_DIR = os.path.join(
    BASE_DIR,
    "static"
)

# Create static folder if missing
os.makedirs(STATIC_DIR, exist_ok=True)

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)

# =========================
# INCLUDE ROUTERS
# =========================

app.include_router(auth_router)

app.include_router(case_router)

app.include_router(timeline_router)

app.include_router(hearing_router)

app.include_router(notification_router)

app.include_router(document_router)

app.include_router(dashboard_router)

app.include_router(websocket_router)

app.include_router(page_router)

# =========================
# PROTECTED ROUTE
# =========================

@app.get("/protected")
def protected_route(
    user_data: dict = Depends(verify_token)
):

    return {
        "message": "Protected route accessed",
        "user": user_data
    }

# =========================
# HOME ROUTE
# =========================

@app.get("/")
def home():

    return {
        "status": "success",
        "message": (
            "Legal Case Management API "
            "Running Successfully"
        )
    }

# =========================
# HEALTH CHECK
# =========================

@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }

# =========================
# RAILWAY STARTUP FIX
# =========================

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 8000)
    )

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )