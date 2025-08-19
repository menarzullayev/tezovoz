# NEW-108
from sqlalchemy import String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base

class Settings(Base):
    """
    Dinamik sozlamalar modeli.
    """
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(255), unique=True)
    value: Mapped[str] = mapped_column(Text)
    is_json: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<Settings(key='{self.key}')>"