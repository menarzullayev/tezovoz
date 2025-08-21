# check_token.py
import asyncio
import sys
from loguru import logger
from aiogram import Bot, exceptions as aiogram_exceptions
from app.config.settings import settings

async def main():
    """Bot tokeni va ulanishini tekshirish uchun asosiy funksiya."""
    try:
        # settings.py faylidan token olinmoqda
        token = settings.BOT_TOKEN.get_secret_value()
        
        # Bot obyektini yaratish
        bot = Bot(token=token)
        
        logger.info("Bot tokeni bilan ulanishga urinish...")
        
        # Oddiy API so'rovini yuborish
        bot_info = await bot.get_me()
        
        logger.success("✅ Bot Telegram API bilan muvaffaqiyatli bog'landi!")
        logger.info(f"Bot nomi: {bot_info.full_name} (@{bot_info.username})")
        
    except aiogram_exceptions.TelegramUnauthorizedError as e:
        logger.critical(f"❌ Xatolik: Bot tokeni noto'g'ri. Iltimos, '.env' faylidagi BOT_TOKENni tekshiring.")
        logger.critical(f"Xato ma'lumoti: {e}")
        sys.exit(1)
        
    except aiogram_exceptions.TelegramNetworkError as e:
        logger.critical(f"❌ Xatolik: Tarmoq ulanishida muammo. Bot serverga ulanishga qiynalmoqda.")
        logger.critical(f"Xato ma'lumoti: {e}")
        sys.exit(1)
        
    except Exception as e:
        logger.critical(f"❌ Kutilmagan xatolik yuz berdi: {e}", exc_info=True)
        sys.exit(1)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    logger.info("Bot tokenini tekshirish skripti ishga tushirildi...")
    asyncio.run(main())