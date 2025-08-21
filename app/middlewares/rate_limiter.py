# FIX-194
# app/middlewares/rate_limiter.py

import asyncio
from typing import Any, Callable, Dict, Awaitable, Optional
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from loguru import logger
from app.config.settings import settings
from app.utils.helpers import extract_user_id

# YANGI: Takroriy ovoz berish uchun cooldown muddatini belgilaymiz (soatda)
VOTE_COOLDOWN_HOURS = 24

class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, default_cooldown_seconds: float = 0.5):
        super().__init__()
        self.default_cooldown_seconds = default_cooldown_seconds
        self.users_cooldowns = {}

    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: Dict[str, Any]) -> Any:
        user_id = extract_user_id(event)

        # Adminlar uchun cheklov ishlamaydi
        if user_id and user_id in settings.ADMIN_IDS:
            return await handler(event, data)

        current_time = asyncio.get_event_loop().time()
        last_request_time = self.users_cooldowns.get(user_id, 0)

        if current_time - last_request_time < self.default_cooldown_seconds:
            await asyncio.sleep(self.default_cooldown_seconds - (current_time - last_request_time))

        self.users_cooldowns[user_id] = asyncio.get_event_loop().time()

        return await handler(event, data)
