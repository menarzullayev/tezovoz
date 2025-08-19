# UPD-107
import asyncio
from loguru import logger
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats
from aiogram import Bot

from app.bot.dispatcher import dp, bot, on_startup, on_shutdown

async def set_bot_commands(bot_instance: Bot):
    """
    Telegram botining asosiy buyruqlarini o'rnatadi.
    """
    commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="account", description="Hisobim"),
        BotCommand(command="help", description="Yordam va ma'lumot"),
    ]
    await bot_instance.set_my_commands(commands, scope=BotCommandScopeAllPrivateChats())
    logger.info("Bot buyruqlari muvaffaqiyatli o'rnatildi.")

async def main():
    """Asosiy ishga tushirish funksiyasi."""
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await set_bot_commands(bot)

    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Botni ishga tushirishda kutilmagan xatolik: {e}", exc_info=True)

if __name__ == "__main__":
    logger.info("Polling skripti ishga tushirildi...")
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot foydalanuvchi tomonidan to'xtatildi.")