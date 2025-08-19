# NEW-112
from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base

class UserActivity(Base):
    """
    Foydalanuvchilarning botdagi faoliyati modeli.
    """
    __tablename__ = "user_activities"

    telegram_id: Mapped[int] = mapped_column(BigInteger, index=True)
    command: Mapped[str] = mapped_column(String(255))
    details: Mapped[str | None] = mapped_column(String(255))

    def __repr__(self) -> str:
        return f"<UserActivity(id={self.id}, telegram_id={self.telegram_id}, command='{self.command}')>"