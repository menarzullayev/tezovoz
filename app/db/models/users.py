# FIX-128
# app/db/models/users.py

from typing import Optional, List
from sqlalchemy import BigInteger, String, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base
from app.db.models.enums import UserStatusEnum

class User(Base):
    """
    Bot foydalanuvchilari modeli.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    username: Mapped[Optional[str]] = mapped_column(String(50))
    phone_number: Mapped[Optional[str]] = mapped_column(String(15), unique=True, nullable=True)
    language_code: Mapped[str] = mapped_column(String(10), default="uz")
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    balance: Mapped[float] = mapped_column(default=0.0)
    user_status: Mapped[UserStatusEnum] = mapped_column(Enum(UserStatusEnum), default=UserStatusEnum.ACTIVE)

    # Barcha bog'liqliklar uchun string forward reference ishlatildi
    referrals: Mapped[List["Referral"]] = relationship(back_populates="referrer", foreign_keys="Referral.referrer_id") #type: ignore
    payments: Mapped[List["Payment"]] = relationship(back_populates="user") #type: ignore
    balance_history: Mapped[List["BalanceHistory"]] = relationship(back_populates="user") #type: ignore
    votes: Mapped[List["Vote"]] = relationship(back_populates="user") #type: ignore
    voting_sessions: Mapped[List["VotingSession"]] = relationship(back_populates="user") #type: ignore

    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username={self.username})>"
