# NEW-109
from sqlalchemy import String, BigInteger, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base

class Contact(Base):
    """
    Foydalanuvchilarning aloqa ma'lumotlari modeli.
    """
    __tablename__ = "contacts"

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    username: Mapped[str | None] = mapped_column(String(50))
    message: Mapped[str] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<Contact(id={self.id}, telegram_id={self.telegram_id})>"