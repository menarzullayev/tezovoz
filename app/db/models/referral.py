# NEW-117
from typing import Optional
from sqlalchemy import ForeignKey, Float, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base
from app.db.models.enums import ReferralStatusEnum

class Referral(Base):
    """
    Referal munosabatlarini saqlash modeli.
    """
    __tablename__ = "referrals"

    referrer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    referred_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    is_active: Mapped[bool] = mapped_column(default=True)
    status: Mapped[ReferralStatusEnum] = mapped_column(Enum(ReferralStatusEnum), default=ReferralStatusEnum.ACTIVE)

    referrer: Mapped["User"] = relationship(foreign_keys=[referrer_id], back_populates="referrals") # type:ignore
    referred: Mapped["User"] = relationship(foreign_keys=[referred_id]) # type:ignore

    def __repr__(self) -> str:
        return f"<Referral(id={self.id}, referrer_id={self.referrer_id})>"