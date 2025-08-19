# FIX-133
# app/handlers/errors.py

from aiogram import Router
from aiogram.types import Update
from loguru import logger
from aiogram.exceptions import TelegramAPIError

router = Router()

@router.errors()
async def handle_errors(update: Update, exception: Exception, *args, **kwargs):
    """
    Dispatcher'dagi barcha kutilmagan xatoliklarni ushlaydigan universal handler.
    Xatolikni logga yozadi va foydalanuvchiga do'stona xabar yuboradi.
    """
    
    # Ba'zi istisnolarni e'tiborsiz qoldirish
    if isinstance(exception, TelegramAPIError) and "message is not modified" in str(exception):
        logger.warning("E'tiborsiz qoldirilgan xatolik: 'message is not modified'")
        return True
    
    # Xatolik haqida batafsil ma'lumotni logga yozish
    payload_data = {
        "exception_type": str(type(exception)),
        "exception_message": str(exception)
    }
    if hasattr(update, 'update_id'):
        payload_data['update_id'] = str(update.update_id)
    
    logger.error(
        f"Kutilmagan xatolik yuz berdi: {exception}", 
        exc_info=True,
        payload=payload_data
    )

    try:
        # Foydalanuvchiga xatolik haqida xabar yuborish
        if isinstance(update, Update) and update.message:
            await update.message.answer("⚠️ Botda kutilmagan xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")
        elif isinstance(update, Update) and update.callback_query:
            await update.callback_query.answer("⚠️ Botda kutilmagan xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")
    except Exception as e:
        logger.error(f"Xato haqida foydalanuvchiga xabar yuborishda xatolik: {e}", exc_info=True)

    # Nima bo'lganini ko'rsatuvchi xabar yuborishni oldini olish uchun True qaytaramiz
    return True
