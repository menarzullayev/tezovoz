# app\db\models\payment.py

# NEW-116
from typing import Optional
from sqlalchemy import Float, ForeignKey, String, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base
from app.db.models.enums import PaymentStatusEnum

class Payment(Base):
    """
    Pul yechish so'rovlari modeli.
    """
    __tablename__ = "payments"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[float] = mapped_column(Float)
    card_number: Mapped[str] = mapped_column(String(20))
    status: Mapped[PaymentStatusEnum] = mapped_column(Enum(PaymentStatusEnum), default=PaymentStatusEnum.PENDING)

    user: Mapped["User"] = relationship(back_populates="payments") #type:ignore

    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, user_id={self.user_id}, amount={self.amount})>"