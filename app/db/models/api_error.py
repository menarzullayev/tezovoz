# NEW-113
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base

class ApiError(Base):
    """
    Openbudget API'dan kelgan xatoliklarni saqlash modeli.
    """
    __tablename__ = "api_errors"

    request_url: Mapped[str] = mapped_column(String(255))
    request_payload: Mapped[str] = mapped_column(Text)
    response_code: Mapped[int] = mapped_column()
    response_body: Mapped[str] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<ApiError(id={self.id}, response_code={self.response_code})>"
