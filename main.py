# FIX-159
import argparse
import asyncio
import sys
from loguru import logger
from aiogram import Bot, Dispatcher, enums
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramAPIError

# Loyihaning asosiy importlari
from app.config.settings import settings
from app.db.session import engine, AsyncSessionLocal, init_db
from app.middlewares import register_all_middlewares
from app.handlers import register_all_handlers
from app.utils.helpers import retry_on_exception, DBConnectionError
from app.handlers.users.language_selection import set_bot_commands_for_all_languages

# Dispatcher va Bot obyektlari bu yerda yaratiladi va global hisoblanadi
bot = Bot(token=settings.BOT_TOKEN.get_secret_value(), default=DefaultBotProperties(parse_mode=enums.ParseMode.HTML))
dp = Dispatcher()


async def on_startup():
    """Bot ishga tushganda bajariladigan amallar."""
    print(">>> DEBUG: on_startup funksiyasiga kirdik.")
    logger.info("on_startup funksiyasi chaqirildi.")

    # 1. Asosiy sozlamalar tekshirilmoqda.
    logger.debug("1. Asosiy sozlamalar tekshirilmoqda.")
    required_settings = ['BOT_TOKEN', 'ADMIN_IDS', 'DB_URL', 'OPENBUDGET_API_URL', 'OPENBUDGET_PROJECT_ID']
    missing_settings = [s for s in required_settings if not getattr(settings, s)]
    if settings.BOT_TOKEN.get_secret_value() == "" or settings.BOT_TOKEN.get_secret_value() == "YOUR_BOT_TOKEN":
        missing_settings.append("BOT_TOKEN")
    if missing_settings:
        logger.critical(f"Konfiguratsiya xatosi: Quyidagi muhim sozlamalar topilmadi: {', '.join(missing_settings)}")
        sys.exit(1)
    logger.debug("Sozlamalar muvaffaqiyatli tekshirildi.")

    # 2. Ma'lumotlar bazasini initsializatsiya qilishga urinish.
    logger.debug("2. Ma'lumotlar bazasini initsializatsiya qilishga urinish.")
    try:
        @retry_on_exception(retries=3, delay=5, exceptions=(DBConnectionError,))
        async def _init_db_with_retry():
            await init_db()
            logger.success("Ma'lumotlar bazasi jadvallari muvaffaqiyatli yaratildi/tekshirildi.")
        
        await _init_db_with_retry()
    except DBConnectionError:
        logger.critical("Ma'lumotlar bazasini initsializatsiya qilishda xatolik. Dastur to'xtatildi.")
        sys.exit(1)
    logger.debug("Ma'lumotlar bazasi initsializatsiyasi tugadi.")
        
    # 3. Bot buyruqlarini o'rnatishga urinish.
    logger.debug("3. Bot buyruqlarini o'rnatishga urinish.")
    try:
        await set_bot_commands_for_all_languages(bot)
        logger.info("Bot buyruqlari o'rnatildi.")
    except TelegramAPIError as e:
        logger.critical(f"Telegram buyruqlarini o'rnatishda xatolik: {e}. Iltimos, BOT_TOKENni tekshiring.", exc_info=True)
        sys.exit(1)
    logger.debug("Bot buyruqlari o'rnatish yakunlandi.")
        
    # 4. Middleware'lar ro'yxatdan o'tkazilmoqda.
    logger.debug("4. Middleware'lar ro'yxatdan o'tkazilmoqda.")
    register_all_middlewares(dp, session_factory=AsyncSessionLocal)
    logger.info("Middleware'lar ro'yxatdan o'tkazildi.")
    logger.debug("Middleware'lar ro'yxatdan o'tkazish yakunlandi.")
    
    # 5. Handler'lar ro'yxatdan o'tkazilmoqda.
    logger.debug("5. Handler'lar ro'yxatdan o'tkazilmoqda.")
    register_all_handlers(dp)
    logger.info("Handler'lar ro'yxatdan o'tkazildi.")
    logger.debug("Handler'lar ro'yxatdan o'tkazish yakunlandi.")
    
    dp.workflow_data["session_factory"] = AsyncSessionLocal
    dp.workflow_data["bot"] = bot
    
    # 6. Webhook'ni o'chirish va kutilayotgan yangilanishlarni tashlab yuborish.
    logger.debug("6. Webhook'ni o'chirish va kutilayotgan yangilanishlarni tashlab yuborish.")
    await bot.delete_webhook(drop_pending_updates=True)
    logger.success("Webhook muvaffaqiyatli o'chirildi va kutilayotgan yangilanishlar tashlab yuborildi.")
    
    logger.success("Bot komponentlari to'liq initsializatsiya qilindi va ishga tushishga tayyor.")
    logger.debug("on_startup funksiyasi yakunlandi.")


async def on_shutdown():
    """Bot to'xtaganda bajariladigan amallar."""
    logger.info("Bot to'xtatilmoqda. Resurslar yopilmoqda...")
    
    logger.debug("1. FSM storage yopilmoqda.")
    await dp.storage.close()
    
    logger.debug("2. Bot sessiyasi yopilmoqda.")
    await bot.session.close()
    
    logger.debug("3. Ma'lumotlar bazasi ulanishi yopilmoqda.")
    if 'engine' in globals() and engine:
        await engine.dispose()
    
    logger.info("Bot to'liq to'xtatildi.")

def parse_args() -> argparse.Namespace:
    """Buyruq qatori argumentlarini parslaydi."""
    parser = argparse.ArgumentParser(description="TezOvoz Telegram Bot.")
    parser.add_argument("--polling", action="store_true", help="Botni polling rejimida ishga tushirish (default).")
    parser.add_argument("--webhook", action="store_true", help="Botni webhook rejimida ishga tushirish.")
    args = parser.parse_args()
    if not (args.polling or args.webhook):
        args.polling = True
    return args


async def main():
    """Asosiy ishga tushirish funksiyasi."""
    args = parse_args()
    
    if args.webhook:
        logger.info("Webhook rejimi tanlandi, ammo hozircha qo'llab-quvvatlanmaydi. Polling rejimida ishlashni davom ettiramiz.")
        args.polling = True

    if args.polling:
        print(">>> DEBUG: start_polling chaqirilishidan oldin.")
        logger.info("Bot polling rejimida ishga tushirildi.")
        try:
            # `on_startup` callback'ini qo'lda chaqirib, so'ngra start_polling'ni ishga tushiramiz
            await on_startup()
            await dp.start_polling(bot, on_shutdown=on_shutdown)
        except (KeyboardInterrupt, SystemExit):
            logger.info("Bot foydalanuvchi tomonidan to'xtatildi.")
        except Exception as e:
            logger.critical(f"Botni ishga tushirishda kutilmagan xatolik: {e}", exc_info=True)
            sys.exit(1)

if __name__ == "__main__":
    logger.info("Polling skripti ishga tushirildi...")
    asyncio.run(main())