# app/handlers/users/help.py

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.db.models.users import User
from app.db.models.faq import Faq
from app.core.constants.i18n_texts import I18nKeys
from aiogram.utils.i18n import I18n

router = Router()

def get_main_help_keyboard(i18n: I18n, locale: str):
    """Yordam bo'limining asosiy tugmasini yaratadi."""
    builder = InlineKeyboardBuilder()
    builder.button(text=i18n.gettext("button-show-faq", locale=locale), callback_data="show_faq")
    return builder.as_markup()

@router.message(F.text.in_([
    "❓ Yordam", "❓ Помощь", "❓ Ёрӣ"
]))
async def handle_help(message: Message, i18n: I18n, user_db: User):
    """"Yordam" tugmasi bosilganda asosiy ma'lumotni va FAQ tugmasini yuboradi."""
    if not message.from_user:
        return
    
    logger.info(f"Foydalanuvchi {user_db.telegram_id} yordam bo'limini so'radi.")
    
    help_text = i18n.gettext(I18nKeys.HELP_MESSAGE, locale=user_db.language_code)
    keyboard = get_main_help_keyboard(i18n, user_db.language_code)
    
    await message.answer(help_text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data == "show_faq")
async def show_faq_questions(callback: CallbackQuery, session: AsyncSession, i18n: I18n, user_db: User):
    """FAQ savollari ro'yxatini inline tugmalar ko'rinishida yuboradi."""
    if not callback.message:
        return

    faqs = await session.scalars(select(Faq).where(Faq.language_code == user_db.language_code))
    
    builder = InlineKeyboardBuilder()
    faq_list = list(faqs) # Skalyar natijani ro'yxatga o'tkazamiz

    if not faq_list:
        await callback.answer(i18n.gettext("faq-no-questions", locale=user_db.language_code), show_alert=True)
        return

    for faq in faq_list:
        builder.button(text=faq.question, callback_data=f"faq:{faq.id}")
    
    builder.adjust(1) # Har bir savolni alohida qatorga joylashtiradi
    
    await callback.message.edit_text(
        text=i18n.gettext("faq-section-title", locale=user_db.language_code),
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("faq:"))
async def show_faq_answer(callback: CallbackQuery, session: AsyncSession, i18n: I18n, user_db: User):
    """Tanlangan FAQ savoliga javobni ko'rsatadi."""
    if not callback.data or not callback.message:
        return
        
    try:
        faq_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer("Xatolik!", show_alert=True)
        return

    faq = await session.get(Faq, faq_id)

    if not faq:
        await callback.answer(i18n.gettext("faq-not-found", locale=user_db.language_code), show_alert=True)
        return

    builder = InlineKeyboardBuilder()
    builder.button(text=i18n.gettext("button-back-to-faq", locale=user_db.language_code), callback_data="show_faq")

    await callback.message.edit_text(
        text=f"<b>Savol:</b> {faq.question}\n\n<b>Javob:</b> {faq.answer}",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()
