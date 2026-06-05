from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey
)

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Case(Base):

    __tablename__ = "cases"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # Unique case reference
    case_number = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    case_title = Column(
        String,
        nullable=False
    )

    case_description = Column(
        Text,
        nullable=False
    )

    case_type = Column(
        String,
        nullable=False,
        default="General"
    )

    case_status = Column(
        String,
        default="Pending",
        nullable=False
    )

    priority = Column(
        String,
        default="Normal",
        nullable=False
    )

    court_name = Column(
        String,
        nullable=True
    )

    client_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    lawyer_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    client = relationship(
        "User",
        foreign_keys=[client_id]
    )

    lawyer = relationship(
        "User",
        foreign_keys=[lawyer_id]
    )

    hearings = relationship(
        "Hearing",
        back_populates="case",
        cascade="all, delete-orphan"
    )

    timeline_events = relationship(
        "TimelineEvent",
        back_populates="case",
        cascade="all, delete-orphan"
    )

    documents = relationship(
        "Document",
        back_populates="case",
        cascade="all, delete-orphan"
    )