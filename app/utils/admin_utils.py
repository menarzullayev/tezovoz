# FIX-176
# app/utils/admin_utils.py

import asyncio
from typing import List
from aiogram import Bot
from loguru import logger
from app.config.settings import settings

async def send_admin_notification(bot: Bot, message_text: str) -> None:
    """
    Barcha adminlarga xabar yuboradi.
    """
    if not settings.ADMIN_IDS:
        logger.warning("Admin IDlari sozlanmagan. Adminlarga xabar yuborilmadi.")
        return

    for admin_id in settings.ADMIN_IDS:
        try:
            await bot.send_message(chat_id=admin_id, text=message_text)
            logger.debug(f"Admin ({admin_id})ga xabar yuborildi.")
        except Exception as e:
            logger.error(f"Admin ({admin_id})ga xabar yuborishda xatolik: {e}", exc_info=False)

async def send_user_status_notification(bot: Bot, user_id: int, message_text: str) -> None:
    """
    Foydalanuvchiga statusi o'zgarganligi haqida xabar yuboradi.
    """
    try:
        await bot.send_message(chat_id=user_id, text=message_text)
        logger.info(f"Foydalanuvchi ({user_id})ga statusi haqida xabar yuborildi.")
    except Exception as e:
        logger.error(f"Foydalanuvchiga ({user_id}) statusi haqida xabar yuborishda xatolik: {e}", exc_info=False)

def get_admin_ids() -> List[int]:
    """
    Sozlamalardan admin IDlar ro'yxatini qaytaradi.
    """
    return settings.ADMIN_IDS