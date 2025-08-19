# NEW-117
from typing import Callable, Dict, Any, Awaitable, Optional
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery, Update
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from app.config.settings import settings
from app.db.models.users import User
from app.db.queries.user_crud_queries import get_user_by_telegram_id, add_user
from app.db.models.enums import UserStatusEnum
from app.utils.helpers import extract_user_id

class UserRegistrationMiddleware(BaseMiddleware):
    """
    Har bir yangilanishda foydalanuvchini ma'lumotlar bazasidan tekshiradi va zarur bo'lsa, ro'yxatdan o'tkazadi.
    """

    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: Dict[str, Any]) -> Any:
        user_id = extract_user_id(event)

        if user_id is None:
            return await handler(event, data)

        session: AsyncSession = data["session"]

        user_db_obj: Optional[User] = await get_user_by_telegram_id(session, user_id)
        is_newly_registered = False

        if user_db_obj is None:
            logger.info(f"Yangi foydalanuvchi aniqlandi: {user_id}. Ro'yxatdan o'tkazilmoqda...")

            user_info = None
            if isinstance(event, Message) or isinstance(event, CallbackQuery):
                user_info = event.from_user
            elif isinstance(event, Update):
                if event.message:
                    user_info = event.message.from_user
                elif event.callback_query:
                    user_info = event.callback_query.from_user

            first_name = user_info.first_name if user_info else "N/A"
            last_name = user_info.last_name if user_info else None
            username = user_info.username if user_info else None
            language_code = settings.DEFAULT_LANGUAGE

            user_db_obj = await add_user(
                session, 
                telegram_id=user_id, 
                first_name=first_name, 
                last_name=last_name, 
                username=username, 
                language_code=language_code,
                user_status=UserStatusEnum.ACTIVE
            )
            is_newly_registered = True
            logger.info(f"Foydalanuvchi {user_id} muvaffaqiyatli ro'yxatdan o'tkazildi.")

        data["user_db"] = user_db_obj
        data["is_new_user"] = is_newly_registered
        logger.debug(f"Middleware yakunlandi. is_new_user: {data['is_new_user']}")

        return await handler(event, data)
