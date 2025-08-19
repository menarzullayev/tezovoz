# NEW-106
import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BigInteger, DateTime, func

class Base(DeclarativeBase):
    """
    Ma'lumotlar bazasi modellarining asosiy sinfi.
    """
    __abstract__ = True
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Umumiy ustunlar
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
