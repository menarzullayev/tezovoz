# app/handlers/users/language_selection.py
# FIX-108: Bot obyektini main.py dan to'g'ri import qilish uchun o'zgartirish
from typing import TYPE_CHECKING
from aiogram import Router, F, Bot, Dispatcher # Dispatcher ham qo'shildi
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery, BotCommand, BotCommandScopeAllPrivateChats
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from app.config.settings import settings
from app.db.queries.user_crud_queries import update_user, get_user_by_telegram_id
from app.db.models.users import User
from app.db.models.referral import Referral
from app.keyboards.inline.language_selection import create_language_selection_keyboard
from app.keyboards.reply.main_menu import create_main_menu_keyboard
from app.core.constants.i18n_texts import I18nKeys
from aiogram.utils.i18n import I18n

if TYPE_CHECKING:
    from typing import Any

router = Router()


async def _show_language_selection_menu(message: Message) -> None:
    """Foydalanuvchiga til tanlash menyusini yuboradi."""
    logger.debug("Debug: _show_language_selection_menu funksiyasi chaqirildi.")
    keyboard = create_language_selection_keyboard()
    formatted_text = "🇺🇿 Tilni tanlang\n🇷🇺 Выберите язык\n🇹🇯 Забонро интихоб кунед"
    await message.answer(text=formatted_text, reply_markup=keyboard, parse_mode=None)
    logger.debug("Debug: Til tanlash menyusi foydalanuvchiga yuborildi.")


async def _show_main_menu(message: Message, i18n: I18n, user_db: User) -> None:
    """Mavjud foydalanuvchiga asosiy menyuni yuboradi."""
    logger.debug("Debug: _show_main_menu funksiyasi chaqirildi.")
    reply_kb = create_main_menu_keyboard(
        gettext_func=lambda text: i18n.gettext(text, locale=user_db.language_code),
        is_admin=user_db.is_admin
    )
    await message.answer(
        text=i18n.gettext(I18nKeys.MAIN_MENU_MESSAGE, locale=user_db.language_code),
        reply_markup=reply_kb
    )
    logger.debug("Debug: Asosiy menyu foydalanuvchiga yuborildi.")


async def set_bot_commands_for_all_languages(bot_instance: Bot):
    """
    Har bir til uchun bot buyruqlarini dinamik ravishda o'rnatadi.
    """
    logger.debug("Debug: set_bot_commands_for_all_languages funksiyasi chaqirildi.")
    i18n_obj = I18n(path=settings.LOCALES_DIR, default_locale=settings.DEFAULT_LANGUAGE, domain=settings.I18N_DOMAIN)
    
    for lang_code in settings.SUPPORTED_LANGUAGES:
        commands = [
            BotCommand(command="start", description=i18n_obj.gettext(I18nKeys.START_MESSAGE_COMMAND, locale=lang_code)),
            BotCommand(command="account", description=i18n_obj.gettext(I18nKeys.ACCOUNT_MESSAGE_COMMAND, locale=lang_code)),
            BotCommand(command="help", description=i18n_obj.gettext(I18nKeys.HELP_MESSAGE_COMMAND, locale=lang_code)),
        ]
        await bot_instance.set_my_commands(commands, scope=BotCommandScopeAllPrivateChats(), language_code=lang_code)

    logger.info("Bot buyruqlari barcha tillar uchun muvaffaqiyatli o'rnatildi.")


@router.message(CommandStart())
async def handle_start(
    message: Message,
    command: CommandObject,
    is_new_user: bool,
    user_db: User,
    session: AsyncSession,
    i18n: I18n,
    bot: Bot
):
    """
    /start buyrug'i uchun handler. Referal havolalarni ham qabul qiladi.
    """
    if not message.from_user:
        logger.warning("Debug: `message.from_user` obyekti topilmadi. Funksiya to'xtatildi.")
        return
        
    logger.info(f"Debug: handle_start funksiyasi chaqirildi. User ID: {message.from_user.id}")

    if is_new_user and command.args and command.args.startswith("ref"):
        logger.debug(f"Debug: Referal mantiqi ishga tushirildi. Args: {command.args}")
        try:
            referrer_id = int(command.args[3:])
            if referrer_id != message.from_user.id:
                logger.debug(f"Debug: Referrer ID: {referrer_id} ni tekshirish.")
                referrer_exists = await session.get(User, referrer_id)
                if referrer_exists:
                    logger.debug(f"Debug: Referrer {referrer_id} mavjud. Bog'liqlik tekshirilmoqda.")
                    referral_exists = await session.scalar(
                        select(Referral).where(
                            Referral.referrer_id == referrer_id,
                            Referral.referred_id == user_db.id
                        )
                    )
                    if not referral_exists:
                        new_referral = Referral(referrer_id=referrer_id, referred_id=user_db.id)
                        session.add(new_referral)
                        await session.commit()
                        logger.info(f"Debug: Yangi referal bog'liqligi saqlandi: {referrer_id} -> {user_db.id}")
                        try:
                            await bot.send_message(
                                referrer_id,
                                i18n.gettext(I18nKeys.NEW_REFERRAL_NOTIFICATION, locale=referrer_exists.language_code)
                            )
                        except Exception as e:
                            logger.error(f"Debug: Referrerga ({referrer_id}) xabar yuborishda xatolik: {e}")
        except (ValueError, IndexError) as e:
            logger.warning(f"Debug: Referal havolani o'qishda xatolik: {command.args} | {e}")

    if is_new_user or not user_db.language_code:
        logger.debug(f"Debug: Yangi foydalanuvchi yoki til o'rnatilmagan. Til tanlash menyusi ko'rsatiladi. is_new_user: {is_new_user}, language_code: {user_db.language_code}")
        await _show_language_selection_menu(message)
    else:
        logger.debug(f"Debug: Mavjud foydalanuvchi. Asosiy menyu ko'rsatiladi. language_code: {user_db.language_code}")
        await _show_main_menu(message, i18n, user_db)
    logger.debug("Debug: handle_start funksiyasi yakunlandi.")


@router.callback_query(F.data.startswith("lang:"))
async def handle_language_selection(callback: CallbackQuery, session: AsyncSession, i18n: I18n):
    if not callback.data or not callback.message or not callback.from_user:
        logger.warning("Debug: Callback data, message yoki from_user mavjud emas.")
        return

    logger.info(f"Debug: handle_language_selection funksiyasi chaqirildi. Callback data: {callback.data}. User ID: {callback.from_user.id}")

    lang_code = callback.data.split(":")[1]
    if lang_code not in settings.SUPPORTED_LANGUAGES:
        logger.warning(f"Debug: Noma'lum til kodi tanlandi: {lang_code}")
        return

    logger.debug(f"Debug: Foydalanuvchi tilini yangilash: {lang_code}")
    await update_user(session, callback.from_user.id, language_code=lang_code)

    user_db = await get_user_by_telegram_id(session, callback.from_user.id)
    if not user_db:
        logger.error(f"Debug: Foydalanuvchi ma'lumotlar bazadan topilmadi. ID: {callback.from_user.id}")
        return

    await callback.answer(i18n.gettext(I18nKeys.LANGUAGE_CHANGED_MESSAGE, locale=lang_code))
    
    if isinstance(callback.message, Message):
        await _show_main_menu(callback.message, i18n, user_db)
    logger.debug("Debug: handle_language_selection funksiyasi yakunlandi.")