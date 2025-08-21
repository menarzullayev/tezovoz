# app/bot/dispatcher.py
# FIX-108
# Bu fayl endi faqat util va helper funksiyalarni saqlaydi, asosiy obyektlar main.py ga ko'chirildi

import sys
from loguru import logger
from aiogram import Bot, Dispatcher
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.config.settings import settings
from app.db.session import engine, AsyncSessionLocal, init_db
from app.middlewares import register_all_middlewares
from app.handlers import register_all_handlers
from app.handlers.users.language_selection import set_bot_commands_for_all_languages
from app.handlers.errors import router as errors_router
from app.utils.helpers import retry_on_exception, DBConnectionError

# FIX-108: `Bot` va `Dispatcher` obyektlari endi `main.py` dan import qilinadi
# Bu fayl faqat handler va middleware'larni ro'yxatdan o'tkazish logikasini saqlaydi
# Bot va Dispatcher yaratilmaydi