from pydantic import BaseModel
from datetime import datetime


class DocumentResponse(BaseModel):

    id: int
    case_id: int
    filename: str
    filepath: str
    uploaded_at: datetime

    class Config:
        from_attributes = True