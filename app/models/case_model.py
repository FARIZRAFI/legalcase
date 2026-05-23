from sqlalchemy import (

    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey
)

from sqlalchemy.sql import (
    func
)

from sqlalchemy.orm import (
    relationship
)

from app.database import Base



class Case(Base):

    __tablename__ = "cases"



    # =========================
    # PRIMARY KEY
    # =========================

    id = Column(

        Integer,

        primary_key=True,

        index=True
    )



    # =========================
    # CASE DETAILS
    # =========================

    case_title = Column(

        String,

        nullable=False
    )



    case_description = Column(

        Text,

        nullable=False
    )



    case_status = Column(

        String,

        default="Pending",

        nullable=False
    )



    # =========================
    # CLIENT & LAWYER
    # =========================

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



    # =========================
    # CREATED AT
    # =========================

    created_at = Column(

        DateTime(timezone=True),

        server_default=func.now()
    )



    # =========================
    # RELATIONSHIPS
    # =========================

    client = relationship(

        "User",

        foreign_keys=[client_id]
    )



    lawyer = relationship(

        "User",

        foreign_keys=[lawyer_id]
    )



    # =========================
    # HEARINGS
    # =========================

    hearings = relationship(

        "Hearing",

        back_populates="case",

        cascade="all, delete-orphan"
    )



    # =========================
    # TIMELINE EVENTS
    # =========================

    timeline_events = relationship(

        "TimelineEvent",

        cascade="all, delete-orphan"
    )



    # =========================
    # DOCUMENTS
    # =========================

    documents = relationship(

        "Document",

        cascade="all, delete-orphan"
    )