from fastapi import FastAPI, Depends

from app.database import engine, Base

# Import Models
from app.models.user_model import User
from app.models.case_model import Case
from app.models.timeline_model import TimelineEvent
from app.models.hearing_model import Hearing
from app.models.notification_model import Notification
from app.models.document_model import Document
from fastapi.staticfiles import StaticFiles

# Import Routers
from app.routes import notification_routes
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

from app.routes import timeline_routes
from app.services.auth_service import verify_token
from app.routes.api_page_routes import router as api_page_router


# Create Database Tables
Base.metadata.create_all(bind=engine)


app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)

# Include Routers
app.include_router(auth_router)

app.include_router(case_router)

app.include_router(timeline_router)

app.include_router(hearing_router)

app.include_router(notification_router)

app.include_router(notification_routes.router)

app.include_router(document_router)

app.include_router(dashboard_router)

app.include_router(websocket_router)

app.include_router(page_router)
app.include_router(timeline_routes.router)

#app.include_router(api_page_router)


# Protected Test Route
@app.get("/protected")
def protected_route(
    user_data: dict = Depends(verify_token)
):

    return {
       "message": "Protected route accessed",
        "user": user_data
    }