from sqlalchemy import String, DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import TYPE_CHECKING


from src.db.base import Base
if TYPE_CHECKING:
    from src.models.task import Task


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="user",
    )
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)