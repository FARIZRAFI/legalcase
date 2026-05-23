from sqlalchemy import (

    Column,
    Integer,
    String,
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



class Hearing(Base):

    __tablename__ = "hearings"



    # =========================
    # PRIMARY KEY
    # =========================

    id = Column(

        Integer,

        primary_key=True,

        index=True
    )



    # =========================
    # CASE RELATION
    # =========================

    case_id = Column(

        Integer,

        ForeignKey(
            "cases.id",
            ondelete="CASCADE"
        ),

        nullable=False
    )



    # =========================
    # HEARING DATE
    # =========================

    hearing_date = Column(

        DateTime(timezone=True),

        nullable=False
    )



    # =========================
    # LOCATION
    # =========================

    location = Column(

        String,

        nullable=False
    )



    # =========================
    # STATUS
    # =========================

    status = Column(

        String,

        default="Scheduled",

        nullable=False
    )



    # =========================
    # CREATED AT
    # =========================

    created_at = Column(

        DateTime(timezone=True),

        server_default=func.now()
    )



    # =========================
    # RELATIONSHIP
    # =========================

    case = relationship(

        "Case",

        back_populates="hearings"
    )