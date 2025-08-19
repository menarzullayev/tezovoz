# app\bot\dispatcher.py
# UPD-106
import asyncio
from pathlib import Path

from aiogram import Bot, Dispatcher, enums
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage # MemoryStorage dan foydalanamiz
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

# Loyihaning o'ziga xos importlari
from app.config.settings import settings
from app.db.session import engine, AsyncSessionLocal, init_db
from app.middlewares import register_all_middlewares
from app.handlers import register_all_handlers
from app.handlers.errors import router as errors_router # Xato handlerlarini qo'shamiz

# Loguru konfiguratsiyasi
# LOG_FILE_PATH - settings.py faylidan olinadi
logger.add(str(settings.LOG_FILE_PATH), format="{time} {level} {message}", level=settings.LOG_LEVEL, rotation="10 MB", compression="zip")

# FSM storage instansiyasini yaratish
# JSONStorage o'rniga MemoryStorage dan foydalanamiz, chunki u lokal rivojlanish uchun oddiyroq
storage: BaseStorage = MemoryStorage()

# Bot va Dispatcher obyektlarini yaratish
bot = Bot(token=settings.BOT_TOKEN.get_secret_value(), default=DefaultBotProperties(parse_mode=enums.ParseMode.HTML))
dp = Dispatcher(storage=storage)


async def on_startup():
    """Bot ishga tushganda bajariladigan amallar."""
    logger.info("Bot ishga tushirilmoqda...")

    # Ma'lumotlar bazasini initsializatsiya qilish
    try:
        await init_db()
        logger.success("Ma'lumotlar bazasi jadvallari muvaffaqiyatli yaratildi/tekshirildi.")
    except Exception as e:
        logger.critical(f"Ma'lumotlar bazasini initsializatsiya qilishda xatolik: {e}", exc_info=True)
        await engine.dispose()
        exit(1)

    # Middleware'larni ro'yxatdan o'tkazish
    register_all_middlewares(dp, session_factory=AsyncSessionLocal)
    logger.info("Middleware'lar ro'yxatdan o'tkazildi.")

    # Handler'larni ro'yxatdan o'tkazish
    register_all_handlers(dp)
    # dp.include_router(errors_router) # Xato handlerini asosiy dispatcherga qo'shdik
    logger.info("Handler'lar ro'yxatdan o'tkazildi.")

    # Muhim obyektlarni dispatcher'ning workflow_data ga qo'shish
    dp.workflow_data["session_factory"] = AsyncSessionLocal
    dp.workflow_data["bot"] = bot

    # Webhook o'chirilmoqda va kutilayotgan yangilanishlar tashlab yuborilmoqda
    await bot.delete_webhook(drop_pending_updates=True)
    logger.success("Webhook muvaffaqiyatli o'chirildi va kutilayotgan yangilanishlar tashlab yuborildi.")

    logger.success("Bot komponentlari to'liq initsializatsiya qilindi va ishga tushishga tayyor.")


async def on_shutdown():
    """Bot to'xtaganda bajariladigan amallar."""
    logger.info("Bot to'xtatilmoqda. Resurslar yopilmoqda...")

    # FSM storage'ni yopish
    await dp.storage.close()

    # Bot sessiyasini yopish
    await bot.session.close()

    # Ma'lumotlar bazasi ulanishini yopish
    await engine.dispose()

    logger.info("Bot to'liq to'xtatildi.")