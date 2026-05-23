import os

from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
    Depends
)

from fastapi.middleware.cors import (
    CORSMiddleware
)

from fastapi.staticfiles import (
    StaticFiles
)

from app.database import (
    engine,
    Base
)



# =========================
# IMPORT MODELS
# =========================

from app.models.user_model import (
    User
)

from app.models.case_model import (
    Case
)

from app.models.timeline_model import (
    TimelineEvent
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



# =========================
# IMPORT ROUTERS
# =========================

from app.routes.auth_routes import (
    router as auth_router
)

from app.routes.case_routes import (
    router as case_router
)

from app.routes.timeline_routes import (
    router as timeline_router
)

from app.routes.hearing_routes import (
    router as hearing_router
)

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



from app.services.auth_service import (
    verify_token
)



# =========================
# BASE DIRECTORY
# =========================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)



# =========================
# STATIC DIRECTORIES
# =========================

STATIC_DIR = os.path.join(
    BASE_DIR,
    "static"
)

UPLOADS_DIR = os.path.join(
    BASE_DIR,
    "uploads"
)



# =========================
# CREATE DIRECTORIES
# =========================

os.makedirs(
    STATIC_DIR,
    exist_ok=True
)

os.makedirs(
    UPLOADS_DIR,
    exist_ok=True
)



# =========================
# APP LIFECYCLE
# =========================

@asynccontextmanager
async def lifespan(app: FastAPI):


    # CREATE DATABASE TABLES
    Base.metadata.create_all(
        bind=engine
    )

    print(
        "Database tables created successfully"
    )

    yield

    print(
        "Application shutdown complete"
    )



# =========================
# CREATE FASTAPI APP
# =========================

app = FastAPI(

    title="Legal Case Management System",

    description="""
    Enterprise Legal Case Management SaaS
    Built using FastAPI + PostgreSQL
    """,

    version="1.0.0",

    lifespan=lifespan
)

@app.get("/")
def root():
    return {"message": "Legal API Running"}



# =========================
# CORS
# =========================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)



# =========================
# STATIC FILES
# =========================

app.mount(

    "/static",

    StaticFiles(directory=STATIC_DIR),

    name="static"
)



# =========================
# UPLOAD FILES
# =========================

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

app.include_router(timeline_router)

app.include_router(hearing_router)

app.include_router(notification_router)

app.include_router(document_router)

app.include_router(dashboard_router)

app.include_router(websocket_router)

app.include_router(page_router)



# =========================
# PROTECTED TEST ROUTE
# =========================

@app.get("/protected")
def protected_route(

    user_data: dict = Depends(
        verify_token
    )
):

    return {

        "message":
        "Protected route accessed",

        "user":
        user_data
    }



# =========================
# API HOME
# =========================

@app.get("/api")
def api_home():

    return {

        "status":
        "success",

        "message":
        "Legal Case Management API Running Successfully"
    }



# =========================
# HEALTH CHECK
# =========================

@app.get("/health")
def health_check():

    return {

        "status":
        "healthy",

        "service":
        "legal-case-management",

        "database":
        "connected"
    }



# =========================
# VERSION
# =========================

@app.get("/version")
def version():

    return {

        "version":
        "1.0.0"
    }
from fastapi.responses import HTMLResponse


