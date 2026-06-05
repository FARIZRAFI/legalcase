from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TimelineBase(BaseModel):
    case_id: int = Field(..., description="The associated legal case ID")
    title: str = Field(..., min_length=1, max_length=200, description="Title of the timeline event")
    description: str = Field(..., description="Detailed logs and field histories of the case update")

class TimelineCreate(TimelineBase):
    pass

class TimelineResponse(TimelineBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True