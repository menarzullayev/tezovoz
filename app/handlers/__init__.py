# app/handlers/__init__.py
# FIX-105

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
    logger.info("Handlerlarni ro'yxatdan o'tkazish boshlandi.")

    logger.debug("Users uchun router yaratilmoqda...")
    users_router = Router()
    logger.debug("Admin uchun router yaratilmoqda...")
    admin_router = Router()

    logger.info("Users handlerlari ro'yxatdan o'tkazilmoqda...")
    try:
        setup_users_handlers(users_router)
        logger.debug("Users handlerlari ro'yxatdan o'tkazish yakunlandi.")
    except Exception as e:
        logger.error(f"Users handlerlarini ro'yxatdan o'tkazishda xatolik: {e}", exc_info=True)
        raise

    logger.info("Admin handlerlari ro'yxatdan o'tkazilmoqda...")
    try:
        setup_admin_handlers(admin_router)
        logger.debug("Admin handlerlari ro'yxatdan o'tkazish yakunlandi.")
    except Exception as e:
        logger.error(f"Admin handlerlarini ro'yxatdan o'tkazishda xatolik: {e}", exc_info=True)
        raise
    
    logger.info("Barcha routerlar asosiy dispatcherga qo'shilmoqda.")
    try:
        dp.include_router(errors_router)
        logger.debug("Errors router qo'shildi.")
        dp.include_router(users_router)
        logger.debug("Users router qo'shildi.")
        dp.include_router(admin_router)
        logger.debug("Admin router qo'shildi.")
    except Exception as e:
        logger.error(f"Routerlarni dispatcherga qo'shishda xatolik: {e}", exc_info=True)
        raise
    
    logger.info("Barcha handlerlar asosiy dispatcherga qo'shildi.")
    logger.debug("Handlerlarni ro'yxatdan o'tkazish to'liq yakunlandi.")