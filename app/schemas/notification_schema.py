from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class NotificationBase(BaseModel):
    user_id: int = Field(..., description="The target user ID to receive the alert")
    title: str = Field(..., min_length=1, max_length=150, description="The headline of the notification")
    message: str = Field(..., min_length=1, description="The detailed message or description text")
    type: str = Field(default="General", description="Classification type (e.g., Hearing, Reschedule, Delete, General)")

class NotificationCreate(NotificationBase):
    pass

class NotificationResponse(NotificationBase):
    id: int
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True