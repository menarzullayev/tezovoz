# NEW-115
from typing import Optional
from sqlalchemy import BigInteger, String, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base
from app.db.models.enums import NotificationStatusEnum

class Notification(Base):
    """
    Foydalanuvchilarga yuboriladigan bildirishnomalar modeli.
    """
    __tablename__ = "notifications"

    message_text: Mapped[str] = mapped_column(Text)
    target_user_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    status: Mapped[NotificationStatusEnum] = mapped_column(Enum(NotificationStatusEnum), default=NotificationStatusEnum.PENDING)

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, status='{self.status.value}')>"
