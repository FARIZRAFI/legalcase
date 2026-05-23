from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)

    case_title = Column(String, nullable=False)

    case_description = Column(Text, nullable=False)

    case_status = Column(String, default="Pending")

    client_id = Column(Integer, ForeignKey("users.id"))

    lawyer_id = Column(Integer, ForeignKey("users.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    client = relationship("User", foreign_keys=[client_id])

    lawyer = relationship("User", foreign_keys=[lawyer_id])