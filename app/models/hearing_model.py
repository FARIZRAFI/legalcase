from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text
)

from sqlalchemy.sql import func

from sqlalchemy.orm import relationship

from app.database import Base


class Hearing(Base):

    __tablename__ = "hearings"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    case_id = Column(
        Integer,
        ForeignKey(
            "cases.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    hearing_date = Column(
        DateTime(timezone=True),
        nullable=False
    )

    location = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        default="Scheduled",
        nullable=False
    )

    judge_name = Column(
        String,
        nullable=True
    )

    remarks = Column(
        Text,
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

    case = relationship(
        "Case",
        back_populates="hearings"
    )