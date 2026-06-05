from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class HearingBase(BaseModel):
    case_id: int = Field(..., description="The ID of the associated legal case")
    hearing_date: datetime = Field(..., description="The date and time of the scheduled hearing")
    location: str = Field(..., min_length=1, max_length=255, description="The courtroom or location of the hearing")
    status: str = Field(default="Scheduled", description="The current status of the hearing (e.g., Scheduled, Adjourned, Completed)")
    
    judge_name: Optional[str] = None

    remarks: Optional[str] = None
class HearingCreate(HearingBase):
    pass

class HearingResponse(HearingBase):
    id: int

    class Config:
        from_attributes = True