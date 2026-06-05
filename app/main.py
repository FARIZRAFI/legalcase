import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import engine, Base
from app.services.auth_service import verify_token

# =========================================================================
# SYSTEMATIC RESTRUCTURING OF ALL SUBSYSTEM DATA MODELS
# =========================================================================
from app.models.user_model import User
from app.models.case_model import Case
from app.models.timeline_model import TimelineEvent
from app.models.hearing_model import Hearing
from app.models.notification_model import Notification
from app.models.document_model import Document

# =========================================================================
# COMPATIBLE BOUND ROUTER REGISTER DIRECTORY
# =========================================================================
from app.routes.auth_routes import router as auth_router
from app.routes.case_routes import router as case_router
from app.routes.timeline_routes import router as timeline_router
from app.routes.hearing_routes import router as hearing_router
from app.routes.notification_routes import router as notification_router
from app.routes.document_routes import router as document_router
from app.routes.dashboard_routes import router as dashboard_router
from app.routes.websocket_routes import router as websocket_router
from app.routes.page_routes import router as page_router

# =========================================================================
# ASSET DIRECTORIES ENGINE MANAGEMENT
# =========================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

# Atomic operating system volume directory check guards
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

# =========================================================================
# ASYNC FASTAPI ECOSYSTEM LIFECYCLE MANAGEMENT
# =========================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQL database table indices safely inside single transaction passes
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
    yield
    print("Application shutdown complete")

app = FastAPI(
    title="Legal Case Management System",
    description="Enterprise Legal Case Management SaaS\nBuilt using FastAPI + PostgreSQL\n",
    version="1.0.0",
    lifespan=lifespan
)

# =========================================================================
# SECURITY POLICIES & NETWORK CROSS-ORIGIN REPLICAS
# =========================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Mount asset volumes straight to native static file servers
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

# =========================================================================
# REGISTER CONTEXT SEGMENT ROUTERS
# =========================================================================

# 1. Root Level Routers (No "/api" prefix)
# This perfectly handles root URLs like "/", "/dashboard-page", and "/auth/login"
app.include_router(page_router)
app.include_router(auth_router)

# 2. Unified API Router Sub-Group (Appends "/api" prefix automatically)
# This solves the routing mismatches for data calls and web sockets
api_router = APIRouter(prefix="/api")

api_router.include_router(case_router)
api_router.include_router(timeline_router)
api_router.include_router(hearing_router)
api_router.include_router(notification_router)
api_router.include_router(document_router)
api_router.include_router(dashboard_router)
api_router.include_router(websocket_router) # Combines /api + /notifications + /ws -> /api/notifications/ws

# Mount the consolidated API routes into the core application engine
app.include_router(api_router)

# =========================================================================
# BASE SYSTEM API ENDPOINTS
# =========================================================================
@app.get("/protected")
def protected_route(user_data: dict = Depends(verify_token)):
    return {"message": "Protected route accessed", "user": user_data}

@app.get("/api")
def api_home():
    return {"status": "success", "message": "Legal Case Management API Running Successfully"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "legal-case-management", "database": "connected"}

@app.get("/version")
def version():
    return {"version": "1.0.0"}