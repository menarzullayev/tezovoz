# NEW-104
import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base
from app.db.models.users import User

class VotingSession(Base):
    """
    Ovoz berish jarayoni uchun vaqtinchalik ma'lumotlar modeli.
    """
    __tablename__ = "voting_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    phone_number: Mapped[str] = mapped_column(String(15))
    captcha_key: Mapped[str] = mapped_column(String(255))
    otp_key: Mapped[Optional[str]] = mapped_column(String(255))
    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship()

    def __repr__(self) -> str:
        return f"<VotingSession(id={self.id}, user_id={self.user_id})>"