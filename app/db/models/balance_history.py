# NEW-114
from typing import Optional
from sqlalchemy import Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base

class BalanceHistory(Base):
    """
    Foydalanuvchi balansi o'zgarishlari tarixi.
    """
    __tablename__ = "balance_histories"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[float] = mapped_column(Float)
    reason: Mapped[str] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)

    user: Mapped["User"] = relationship(back_populates="balance_history") #type:ignore

    def __repr__(self) -> str:
        return f"<BalanceHistory(id={self.id}, user_id={self.user_id}, amount={self.amount})>"