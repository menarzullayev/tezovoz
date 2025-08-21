# app/handlers/users/__init__.py
# FIX-105

from aiogram import Router
from loguru import logger # NEW-105: loguru import qilindi

from .language_selection import router as lang_router
from .start_vote import router as start_vote_router
from .auto_vote_handlers import router as auto_vote_router
from .manual_vote_handlers import router as manual_vote_router
from .account import router as account_router
from .referral import router as referral_router
from .help import router as help_router

def setup_users_handlers(router: Router):
    """
    Foydalanuvchilarga oid barcha handlerlarni ro'yxatdan o'tkazadi.
    """
    logger.debug("setup_users_handlers chaqirildi.")
    router.include_router(lang_router)
    logger.debug("lang_router qo'shildi.")
    router.include_router(start_vote_router)
    logger.debug("start_vote_router qo'shildi.")
    router.include_router(auto_vote_router)
    logger.debug("auto_vote_router qo'shildi.")
    router.include_router(manual_vote_router)
    logger.debug("manual_vote_router qo'shildi.")
    router.include_router(account_router)
    logger.debug("account_router qo'shildi.")
    router.include_router(referral_router)
    logger.debug("referral_router qo'shildi.")
    router.include_router(help_router)
    logger.debug("help_router qo'shildi.")
    logger.debug("setup_users_handlers yakunlandi.")