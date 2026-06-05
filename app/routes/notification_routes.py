from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.notification_model import Notification
from app.services.auth_service import verify_token
from app.core.websocket import manager

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    # Authenticate
    user_data = verify_token(token)
    if not user_data:
        await websocket.close(code=1008)
        return

    user_id = user_data["user_id"]
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            await websocket.receive_text() # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(user_id)

@router.get("/")
def get_notifications(db: Session = Depends(get_db), user_data: dict = Depends(verify_token)):
    return db.query(Notification).filter(Notification.user_id == user_data["user_id"]).order_by(Notification.id.desc()).all()

@router.put("/{notification_id}")
def mark_notification_read(notification_id: int, db: Session = Depends(get_db), user_data: dict = Depends(verify_token)):
    notification = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user_data["user_id"]).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Not found")
    
    notification.is_read = True
    db.commit()
    return {"message": "Marked as read"}