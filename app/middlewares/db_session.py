# NEW-114
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from app.utils.helpers import extract_user_id

class DbSessionMiddleware(BaseMiddleware):
    """
    Har bir yangilanish (Update) uchun ma'lumotlar bazasi sessiyasini ta'minlaydi.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__()
        self.session_factory = session_factory
        logger.info("DbSessionMiddleware initsializatsiya qilindi.")

    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: Dict[str, Any]) -> Any:
        user_id = extract_user_id(event)
        event_type = type(event).__name__

        logger.debug(f"DEBUG: Middlewarega yangilanish keldi. Event turi: {event_type}. User ID: {user_id}")

        async with self.session_factory() as session:
            data["session"] = session
            try:
                result = await handler(event, data)
                await session.commit()
                return result
            except SQLAlchemyError as e:
                logger.error("Ma'lumotlar bazasi xatosi: {}", e, exc_info=True)
                await session.rollback()
                raise