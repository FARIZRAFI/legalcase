from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey
)

from sqlalchemy.sql import func
from app.database import Base 

class Notification(Base):

    __tablename__ = "notifications"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    title = Column(
        String,
        nullable=False
    )

    message = Column(
        String,
        nullable=False
    )

    type = Column(
        String,
        nullable=False
    )

    action_url = Column(
        String,
        nullable=True
    )

    is_read = Column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )