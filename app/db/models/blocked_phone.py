# NEW-111
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base

class BlockedPhone(Base):
    """
    Bloklangan telefon raqamlari modeli.
    """
    __tablename__ = "blocked_phones"

    phone_number: Mapped[str] = mapped_column(String(15), unique=True)
    reason: Mapped[str | None] = mapped_column(String(255))

    def __repr__(self) -> str:
        return f"<BlockedPhone(phone_number='{self.phone_number}')>"