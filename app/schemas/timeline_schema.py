from pydantic import BaseModel
from datetime import datetime


class TimelineCreate(BaseModel):

    case_id: int
    title: str
    description: str


class TimelineResponse(BaseModel):

    id: int
    case_id: int
    title: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True