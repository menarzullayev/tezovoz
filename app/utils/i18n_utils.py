# FIX-119
# app/utils/i18n_utils.py

from typing import Any, Dict, Optional, Callable, Awaitable
from aiogram import BaseMiddleware, Dispatcher
from aiogram.types import TelegramObject
from aiogram.utils.i18n import I18n as AiogramI18n
from loguru import logger
from pathlib import Path

# Babel kutubxonasini to'g'ri import qilamiz
from babel.support import Translations

from app.db.models.users import User
from app.config.settings import settings

class I18nMiddleware(BaseMiddleware):
    """
    Foydalanuvchi tilini aniqlaydi va handlerlarga I18nContext obyektini uzatadi.
    """

    def __init__(self, i18n: AiogramI18n):
        super().__init__()
        self.i18n = i18n

    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: Dict[str, Any]) -> Any:
        user_db: Optional[User] = data.get("user_db")
        locale = settings.DEFAULT_LANGUAGE

        if user_db and user_db.language_code:
            locale = user_db.language_code

        data["i18n"] = self.i18n
        data["locale"] = locale
        
        logger.debug(f"I18nMiddleware: Foydalanuvchi tili {locale} deb o'rnatildi.")
        
        with self.i18n.context(), self.i18n.use_locale(locale):
            return await handler(event, data)


def setup_i18n_middleware(dp: Dispatcher):
    """
    Babel yordamida I18n middleware'ni sozlaydi va ro'yxatdan o'tkazadi.
    """
    try:
        # I18n klassi tarjimalarni avtomatik tarzda topadi
        i18n = AiogramI18n(
            path=str(settings.LOCALES_DIR),
            default_locale=settings.DEFAULT_LANGUAGE
        )

        dp.update.middleware(I18nMiddleware(i18n))
        logger.info("Babel asosida i18n middleware muvaffaqiyatli ro'yxatdan o'tkazildi.")
                
    except Exception as e:
        logger.critical(f"Babel asosida I18n middleware'ni sozlashda kutilmagan xatolik yuz berdi: {e}", exc_info=True)