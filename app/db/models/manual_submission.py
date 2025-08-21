# app/db/models/manual_submission.py

from sqlalchemy import BigInteger, String, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.models.base import Base
import enum

class SubmissionStatusEnum(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class ManualSubmission(Base):
    __tablename__ = "manual_submissions"

    user_id: Mapped[int] = mapped_column(BigInteger)
    telegram_file_id: Mapped[str] = mapped_column(String(255))
    status: Mapped[SubmissionStatusEnum] = mapped_column(
        Enum(SubmissionStatusEnum), default=SubmissionStatusEnum.PENDING, index=True
    )

    # User modeliga bog'liqlik (ixtiyoriy, lekin yaxshi amaliyot)
    user: Mapped["User"] = relationship(foreign_keys=[user_id], primaryjoin="ManualSubmission.user_id == User.telegram_id") #type: ignore
