from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
)

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
        ForeignKey("cases.id")
    )

    hearing_date = Column(
        DateTime
    )

    location = Column(
        String
    )

    status = Column(
        String,
        default="Scheduled"
    )