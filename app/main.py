import os

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles

from app.database import engine, Base

# =========================
# IMPORT MODELS
# =========================

from app.models.user_model import User
from app.models.case_model import Case
from app.models.timeline_model import TimelineEvent
from app.models.hearing_model import Hearing
from app.models.notification_model import Notification
from app.models.document_model import Document

# =========================
# IMPORT ROUTERS
# =========================

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

# =========================
# CREATE DATABASE TABLES
# =========================

Base.metadata.create_all(bind=engine)

# =========================
# CREATE FASTAPI APP
# =========================

app = FastAPI(
    title="Legal Case Management System"
)

# =========================
# STATIC FILES
# =========================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

STATIC_DIR = os.path.join(
    BASE_DIR,
    "static"
)

UPLOADS_DIR = os.path.join(
    BASE_DIR,
    "uploads"
)

# Create folders if missing
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Mount Static Folder
app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)

# Mount Uploads Folder
app.mount(
    "/uploads",
    StaticFiles(directory=UPLOADS_DIR),
    name="uploads"
)

# =========================
# INCLUDE ROUTERS
# =========================

app.include_router(auth_router)

app.include_router(case_router)

#app.include_router(timeline_router)

app.include_router(hearing_router)

#app.include_router(notification_router)

app.include_router(document_router)

app.include_router(dashboard_router)

#app.include_router(websocket_router)

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