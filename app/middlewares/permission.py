# NEW-115
from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from loguru import logger
from app.config.settings import settings
from app.utils.helpers import extract_user_id

class PermissionMiddleware(BaseMiddleware):
    """
    Foydalanuvchining adminlik huquqini tekshiradi va is_admin kalitini data lug'atiga qo'shadi.
    """

    def __init__(self):
        super().__init__()
        self.admin_ids_set = set(settings.ADMIN_IDS)
        logger.info("PermissionMiddleware initsializatsiya qilindi.")

    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: Dict[str, Any]) -> Any:
        user_id = extract_user_id(event)

        is_admin = False
        if user_id and user_id in self.admin_ids_set:
            is_admin = True

        data["is_admin"] = is_admin
        logger.debug(f"Foydalanuvchi {user_id} adminlik huquqi: {is_admin}")

        return await handler(event, data)
