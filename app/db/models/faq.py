# NEW-107
from sqlalchemy import Text, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base

class Faq(Base):
    """
    Tez-tez beriladigan savollar modeli.
    """
    __tablename__ = "faq"

    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    language_code: Mapped[str] = mapped_column(String(10))

    def __repr__(self) -> str:
        return f"<Faq(id={self.id}, question='{self.question[:20]}...')>"