# NEW-126
# app/handlers/__init__.py

from aiogram import Router, Dispatcher
from loguru import logger

# Handlerlarni import qilamiz
from .users import setup_users_handlers
from .admin import setup_admin_handlers
from .errors import router as errors_router


def register_all_handlers(dp: Dispatcher):
    """
    Barcha handlerlarni ro'yxatdan o'tkazadi.
    """
    users_router = Router()
    admin_router = Router()

    logger.info("Handlerlarni ro'yxatdan o'tkazish boshlandi.")

    # Handlerlarni vazifalari bo'yicha guruhlaymiz
    logger.info("Users handlerlari ro'yxatdan o'tkazilmoqda...")
    setup_users_handlers(users_router)
    logger.info("Admin handlerlari ro'yxatdan o'tkazilmoqda...")
    setup_admin_handlers(admin_router)
    
    # Barcha routerlarni asosiy dispatcherga to'g'ridan-to'g'ri qo'shamiz
    dp.include_router(errors_router)
    dp.include_router(users_router)
    dp.include_router(admin_router)
    
    logger.info("Barcha handlerlar asosiy dispatcherga qo'shildi.")