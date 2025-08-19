# NEW-121
# app/db/session.py

from typing import AsyncGenerator, Dict, Any
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
from app.config.settings import settings
from app.db.models.base import Base

def create_async_db_engine() -> AsyncEngine:
    """SQLAlchemy Asinxron Engine obyektini yaratadi va qaytaradi."""
    engine_args: Dict[str, Any] = {
        "echo": settings.DB_ECHO,
        "future": True
    }
    
    try:
        engine: AsyncEngine = create_async_engine(settings.DB_URL, **engine_args)
        return engine
    except Exception as e:
        logger.critical(f"Ma'lumotlar bazasi engine'ini yaratishda kutilmagan xatolik: {e}", exc_info=True)
        # Ma'lumotlar bazasiga ulanishning iloji bo'lmasa, ilovadan chiqib ketishimiz kerak
        exit(1)

engine: AsyncEngine = create_async_db_engine()

# --- Asinxron Session Maker obyektini yaratish ---
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    """
    Ma'lumotlar bazasini initsializatsiya qiladi va barcha jadvallarni yaratadi.
    """
    logger.info("Ma'lumotlar bazasi jadvallarini yaratish boshlandi.")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Ma'lumotlar bazasi jadvallari muvaffaqiyatli yaratildi.")
    except SQLAlchemyError as e:
        logger.critical(f"Ma'lumotlar bazasi jadvallarini yaratishda SQLAlchemy xatolik: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.critical(f"Ma'lumotlar bazasi jadvallarini yaratishda kutilmagan muhim xatolik yuz berdi: {e}", exc_info=True)
        raise
