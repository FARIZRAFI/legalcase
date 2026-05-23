from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# Create Case Schema
class CaseCreate(BaseModel):
    case_title: str
    case_description: str
    client_id: int
    lawyer_id: int


# Update Case Schema
class CaseUpdate(BaseModel):
    case_title: Optional[str] = None
    case_description: Optional[str] = None
    case_status: Optional[str] = None
    lawyer_id: Optional[int] = None


# Response Schema
class CaseResponse(BaseModel):
    id: int
    case_title: str
    case_description: str
    case_status: str
    client_id: int
    lawyer_id: int
    created_at: datetime

    class Config:
        from_attributes = True