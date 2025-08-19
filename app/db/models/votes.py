# FIX-129
# app/db/models/votes.py

import datetime
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base

class Vote(Base):
    """
    Muvaffaqiyatli ovozlar modeli.
    """
    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    phone_number: Mapped[str] = mapped_column(String(15))
    voted_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=datetime.datetime.now(datetime.timezone.utc))
    project_id: Mapped[Optional[int]] = mapped_column(Integer, default=0)

    # Userga bog'liqlik uchun string forward reference ishlatildi
    user: Mapped["User"] = relationship(back_populates="votes")

    def __repr__(self) -> str:
        return f"<Vote(id={self.id}, user_id={self.user_id})>"
