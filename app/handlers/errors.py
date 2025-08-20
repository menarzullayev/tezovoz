# FIX-133 (Yakuniy versiya, aiogram 3.x uchun to'liq moslashtirilgan)
# app/handlers/errors.py

from aiogram import Router, Bot
from aiogram.types.error_event import ErrorEvent
from loguru import logger
from aiogram.exceptions import TelegramAPIError
import traceback

router = Router()

@router.errors()
async def handle_errors(event: ErrorEvent, bot: Bot):
    """
    Dispatcher'dagi barcha kutilmagan xatoliklarni ushlaydigan universal handler.
    """
    update = event.update
    exception = event.exception

    if isinstance(exception, TelegramAPIError) and "message is not modified" in str(exception):
        logger.warning("E'tiborsiz qoldirilgan xatolik: 'message is not modified'")
        return True
    
    logger.error(
        f"Update id={update.update_id} da kutilmagan xatolik yuz berdi: {exception}\n{traceback.format_exc()}"
    )

    try:
        chat_id = None
        if update.message:
            chat_id = update.message.chat.id
        elif update.callback_query:
            chat_id = update.callback_query.from_user.id
        
        if chat_id:
             await bot.send_message(
                 chat_id,
                 "⚠️ Botda kutilmagan xatolik yuz berdi. Iltimos, /start tugmasini bosib, qaytadan urinib ko'ring."
            )
    except Exception as e:
        logger.error(f"Xato haqida foydalanuvchiga xabar yuborishning o'zida xatolik: {e}", exc_info=True)

    return True
