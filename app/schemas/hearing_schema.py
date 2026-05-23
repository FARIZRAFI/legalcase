from pydantic import BaseModel
from datetime import datetime


class HearingCreate(BaseModel):

    case_id: int

    hearing_date: datetime

    location: str

    status: str


class HearingResponse(BaseModel):

    id: int

    case_id: int

    hearing_date: datetime

    location: str

    status: str

    class Config:

        from_attributes = True