# UPD-111
# app/handlers/users/__init__.py

from aiogram import Router

from .language_selection import router as lang_router
from .voting import router as voting_router
# from .account import router as account_router # Hali yaratilmagan

def setup_users_handlers(router: Router):
    """
    Foydalanuvchilarga oid barcha handlerlarni ro'yxatdan o'tkazadi.
    """
    router.include_router(lang_router)
    router.include_router(voting_router)
    # router.include_router(account_router)