# NEW-112
import asyncio
from functools import wraps
from typing import Any, Awaitable, Type, Tuple, Callable, Optional, Union, List, Generator
from loguru import logger
from aiogram.types import TelegramObject, Message, CallbackQuery, InlineQuery, ChatMemberUpdated, ChatJoinRequest, Update

def retry_on_exception(retries: int = 3, delay: float = 1.0, exceptions: Tuple[Type[Exception], ...] = (Exception,)):
    """
    Xatolik yuz berganda funksiyani qayta chaqirish uchun dekorator.
    """
    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            for i in range(retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    logger.warning(f"'{func.__name__}' funksiyasida xatolik yuz berdi ({type(e).__name__}: {e}). Qayta urinish ({i + 1}/{retries})...", exc_info=True)
                    if i < retries - 1:
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"'{func.__name__}' funksiyasi {retries} urinishdan so'ng muvaffaqiyatsiz tugadi.", exc_info=True)
                        raise
        return wrapper
    return decorator


def extract_user_id(event: TelegramObject) -> Optional[int]:
    """
    Berilgan TelegramObject'dan foydalanuvchi ID'sini ajratib oladi.
    """
    from_user = None
    if isinstance(event, Message):
        from_user = event.from_user
    elif isinstance(event, CallbackQuery):
        from_user = event.from_user
    elif isinstance(event, InlineQuery):
        from_user = event.from_user
    elif isinstance(event, ChatMemberUpdated):
        from_user = event.from_user
    elif isinstance(event, ChatJoinRequest):
        from_user = event.from_user
    elif isinstance(event, Update):
        if event.message:
            from_user = event.message.from_user
        elif event.callback_query:
            from_user = event.callback_query.from_user
    
    return from_user.id if from_user else None