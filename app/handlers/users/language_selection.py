# FIX-130
# app/handlers/users/language_selection.py

from typing import Optional, Any, Callable
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from app.config.settings import settings
from app.db.queries.user_crud_queries import update_user, get_user_by_telegram_id
from app.db.models.users import User
from app.keyboards.inline.language_selection import create_language_selection_keyboard
from app.keyboards.reply.main_menu import create_main_menu_keyboard
from app.core.constants.i18n_texts import I18nKeys
from aiogram.utils.i18n import gettext as _, I18n as AiogramI18n
from babel.support import Translations

router = Router()

async def _show_language_selection_menu(message: Message, i18n: Any) -> None:
    """
    Foydalanuvchiga til tanlash menyusini yuboradi.
    """
    logger.debug("Til tanlash menyusi yuborilmoqda.")
    keyboard = create_language_selection_keyboard()

    formatted_text = "🇺🇿 Tilni tanlang\n🇷🇺 Выберите язык\n🇹🇯 Забонро интихоб кунед"

    await message.answer(
        text=formatted_text,
        reply_markup=keyboard,
        parse_mode=None
    )
    logger.debug("Til tanlash menyusi yuborildi.")

async def _show_main_menu(message: Message, i18n: AiogramI18n, user_db: User, bot: Bot) -> None:
    """
    Mavjud foydalanuvchiga asosiy menyuni yuboradi.
    """
    logger.debug(f"Asosiy menyu '{user_db.language_code}' tilida ko'rsatilmoqda.")
    
    # gettext_func parametrini to'g'ri uzatamiz
    reply_kb = create_main_menu_keyboard(gettext_func=i18n.gettext, is_admin=user_db.is_admin)

    await message.answer(
        text=i18n.gettext(I18nKeys.MAIN_MENU_MESSAGE),
        reply_markup=reply_kb
    )
    logger.debug("Asosiy menyu yuborildi.")


@router.message(CommandStart())
async def handle_start(
    message: Message, 
    is_new_user: bool, 
    user_db: Optional[User], 
    session: AsyncSession, 
    i18n: AiogramI18n, 
    bot: Bot
):
    """
    /start buyrug'i uchun handler.
    """
    user = message.from_user
    if not user:
        logger.warning("Foydalanuvchi ma'lumoti mavjud emas.")
        return

    logger.info(f"{user.id} - /start buyrug'ini yubordi. Yangi foydalanuvchi: {is_new_user}")

    if is_new_user or user_db is None or user_db.language_code is None:
        await _show_language_selection_menu(message, i18n)
    else:
        await _show_main_menu(message, i18n, user_db, bot)


@router.callback_query(F.data.startswith("lang:"))
async def handle_language_selection(
    callback: CallbackQuery, 
    session: AsyncSession, 
    i18n: AiogramI18n, 
    bot: Bot,
):
    """
    Tilni tanlash tugmasi bosilganda ishga tushadigan callback handler.
    """
    user = callback.from_user
    if not callback.data or not callback.message or not user:
        logger.warning("Callback ma'lumotlari to'liq emas.")
        await callback.answer(i18n.gettext(I18nKeys.ERROR_OCCURRED), show_alert=True)
        return

    logger.info(f"{user.id} - Tilni tanlash tugmasi bosildi. Callback data: {callback.data}")

    lang_code = callback.data.split(":")[1]
    user_id = user.id

    if lang_code not in settings.SUPPORTED_LANGUAGES:
        await callback.answer(i18n.gettext(I18nKeys.UNKNOWN_COMMAND_MESSAGE), show_alert=True)
        logger.warning(f"{user_id} - noto‘g‘ri til tanladi: {lang_code}")
        return

    await update_user(session, user_id, language_code=lang_code)

    # Yangi til uchun tarjimani to'g'ridan-to'g'ri Babel'dan olamiz.
    new_translations = Translations.load(
        dirname=str(settings.LOCALES_DIR),
        locales=[lang_code],
        domain=settings.I18N_DOMAIN
    )
    new_i18n_runner: Callable[[str], str] = new_translations.gettext
    
    await callback.answer(new_i18n_runner(I18nKeys.LANGUAGE_CHANGED_MESSAGE), show_alert=False)

    user_db = await get_user_by_telegram_id(session, user_id)
    if not user_db:
        logger.error(f"Foydalanuvchi {user_id} tilni tanlaganidan keyin topilmadi.")
        await callback.answer(new_i18n_runner(I18nKeys.ERROR_OCCURRED), show_alert=True)
        return
        
    await _show_main_menu(message=callback.message, i18n=i18n, user_db=user_db, bot=bot)