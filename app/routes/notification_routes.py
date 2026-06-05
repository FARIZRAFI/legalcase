from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.notification_model import Notification
from app.services.auth_service import verify_token
from app.core.websocket import manager  # Imported cleanly from core

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.get("/")
def get_notifications(db: Session = Depends(get_db), user_data: dict = Depends(verify_token)):
    return db.query(Notification).filter(Notification.user_id == user_data["user_id"]).order_by(Notification.id.desc()).all()

@router.put("/{notification_id}")
def mark_notification_read(notification_id: int, db: Session = Depends(get_db), user_data: dict = Depends(verify_token)):
    notification = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user_data["user_id"]).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification.is_read = True
    db.commit()
    return {"message": "Notification marked as read"}