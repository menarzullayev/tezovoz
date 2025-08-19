# NEW-110
from sqlalchemy import String, Float, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base

class Promocode(Base):
    """
    Promokodlar modeli.
    """
    __tablename__ = "promocodes"

    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    value: Mapped[float] = mapped_column(Float, default=0.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    usage_limit: Mapped[int] = mapped_column(Integer, default=1)
    used_count: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self) -> str:
        return f"<Promocode(code='{self.code}', value={self.value})>"