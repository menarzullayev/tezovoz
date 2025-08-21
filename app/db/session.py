# app/db/session.py
# FIX-106

from typing import AsyncGenerator, Dict, Any
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
from app.config.settings import settings
from app.db.models.base import Base

def create_async_db_engine() -> AsyncEngine:
    """SQLAlchemy Asinxron Engine obyektini yaratadi va qaytaradi."""
    logger.debug("Debug: Asinxron DB engine yaratishga urinish...")
    engine_args: Dict[str, Any] = {
        "echo": settings.DB_ECHO,
        "future": True
    }
    
    try:
        engine: AsyncEngine = create_async_engine(settings.DB_URL, **engine_args)
        logger.debug("Debug: Asinxron DB engine muvaffaqiyatli yaratildi.")
        return engine
    except Exception as e:
        logger.critical(f"Ma'lumotlar bazasi engine'ini yaratishda kutilmagan xatolik: {e}", exc_info=True)
        # Ma'lumotlar bazasiga ulanishning iloji bo'lmasa, ilovadan chiqib ketishimiz kerak
        exit(1)

engine: AsyncEngine = create_async_db_engine()
logger.debug("Debug: Global 'engine' obyekti o'rnatildi.")

# --- Asinxron Session Maker obyektini yaratish ---
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
logger.debug("Debug: Global 'AsyncSessionLocal' obyekti o'rnatildi.")


async def init_db():
    """
    Ma'lumotlar bazasini initsializatsiya qiladi va barcha jadvallarni yaratadi.
    """
    logger.info("Ma'lumotlar bazasi jadvallarini yaratish boshlandi.")
    try:
        logger.debug("Debug: Engine bilan ulanish va tranzaksiyani boshlash.")
        async with engine.begin() as conn:
            logger.debug("Debug: create_all buyrug'ini sinxron bajarish.")
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Ma'lumotlar bazasi jadvallari muvaffaqiyatli yaratildi.")
    except SQLAlchemyError as e:
        logger.critical(f"Ma'lumotlar bazasi jadvallarini yaratishda SQLAlchemy xatolik: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.critical(f"Ma'lumotlar bazasi jadvallarini yaratishda kutilmagan muhim xatolik yuz berdi: {e}", exc_info=True)
        raise