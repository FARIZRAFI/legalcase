from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class CaseBase(BaseModel):
    case_title: str = Field(..., min_length=1, max_length=255, description="The official name or title of the lawsuit")
    case_number: str = Field(..., min_length=1, max_length=100, description="Unique legal court index tracking identifier")
    case_description: Optional[str] = Field(None, description="Detailed background or notes regarding the lawsuit context")
    case_status: str = Field(default="Active", description="Current status of the case (e.g., Active, Closed, Pending, Appealed)")
    client_id: int = Field(..., description="The ID of the client user attached to this legal matter")

class CaseCreate(CaseBase):
    pass

class CaseUpdate(BaseModel):
    case_title: Optional[str] = None
    case_number: Optional[str] = None
    case_description: Optional[str] = None
    case_status: Optional[str] = None
    client_id: Optional[int] = None

class CaseResponse(CaseBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True