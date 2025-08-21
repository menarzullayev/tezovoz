# app\middlewares\__init__.py

# NEW-118
from aiogram import Dispatcher
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.middlewares.db_session import DbSessionMiddleware
from app.middlewares.user_registration import UserRegistrationMiddleware
from app.utils.i18n_utils import setup_i18n_middleware
from app.middlewares.permission import PermissionMiddleware
from app.middlewares.rate_limiter import RateLimitMiddleware


def register_all_middlewares(dp: Dispatcher, session_factory: async_sessionmaker[AsyncSession]):
    """
    Barcha middleware'larni ro'yxatdan o'tkazadi.
    """
    dp.update.middleware(DbSessionMiddleware(session_factory=session_factory))
    dp.update.middleware(UserRegistrationMiddleware())
    dp.update.middleware(PermissionMiddleware())
    dp.update.middleware(RateLimitMiddleware())
    
    setup_i18n_middleware(dp)
