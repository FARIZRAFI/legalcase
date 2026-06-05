from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class DocumentBase(BaseModel):
    case_id: int = Field(..., description="The ID of the associated legal case this document belongs to")
    filename: str = Field(..., min_length=1, max_length=255, description="The original filename of the uploaded file")
    filepath: str = Field(..., min_length=1, description="The local storage path or cloud URL bucket key of the saved file")

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(DocumentBase):
    id: int
    uploaded_at: datetime

    class Config:
        from_attributes = True