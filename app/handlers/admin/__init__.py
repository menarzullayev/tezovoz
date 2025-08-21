# FIX-202
# app/handlers/admin/__init__.py

from aiogram import Router, F
from loguru import logger 
from .settings_handler import router as settings_router
from .verification_handler import router as verification_router
from .payment_verification import router as payment_verification_router
from .stats import router as stats_router
from .messaging import router as messaging_router
from .user_management import router as user_management_router
from .admin_panel import router as admin_panel_router # Yangi import
from app.middlewares.permission import PermissionMiddleware

def setup_admin_handlers(router: Router):
    logger.debug("setup_admin_handlers chaqirildi.")
    admin_router = Router()
    
    logger.debug("Admin routeriga middleware va filterlar qo'shilmoqda.")
    admin_router.message.middleware(PermissionMiddleware())
    admin_router.message.filter(F.is_admin == True)
    admin_router.callback_query.middleware(PermissionMiddleware())
    admin_router.callback_query.filter(F.is_admin == True)

    logger.debug("Ichki admin routerlari qo'shilmoqda.")
    admin_router.include_router(settings_router)
    logger.debug("settings_router qo'shildi.")
    admin_router.include_router(verification_router)
    logger.debug("verification_router qo'shildi.")
    admin_router.include_router(payment_verification_router)
    logger.debug("payment_verification_router qo'shildi.")
    admin_router.include_router(stats_router)
    logger.debug("stats_router qo'shildi.")
    admin_router.include_router(messaging_router)
    logger.debug("messaging_router qo'shildi.")
    admin_router.include_router(user_management_router)
    logger.debug("user_management_router qo'shildi.")
    
    # Asosiy admin routerini qo'shish
    admin_router.include_router(admin_panel_router) # Yangi router qo'shildi
    logger.debug("admin_panel_router qo'shildi.")

    logger.debug("Asosiy routerga admin_routerni qo'shish.")
    router.include_router(admin_router)
    logger.debug("setup_admin_handlers yakunlandi.")