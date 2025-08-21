# NEW-201
# app/handlers/admin/admin_panel.py

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.i18n import I18n

from app.db.models.users import User
from app.core.constants.i18n_buttons import I18nButtons
from app.core.constants.i18n_texts import I18nKeys
from app.keyboards.reply.admin_menu import create_admin_menu_keyboard

router = Router()

@router.message(Command(commands=["admin"]))
@router.message(F.text.in_([
    "🤖 Admin Paneli", "🤖 Админ-панель", "🤖 Панели администратор"
]))
async def show_admin_panel(message: Message, i18n: I18n, user_db: User):
    """
    Adminlar uchun asosiy admin panel menyusini ko'rsatadi.
    """
    if not user_db.is_admin:
        await message.answer(i18n.gettext(I18nKeys.NO_PERMISSION, locale=user_db.language_code))
        return
        
    await message.answer(
        i18n.gettext(I18nKeys.ADMIN_PANEL_MESSAGE, locale=user_db.language_code),
        reply_markup=create_admin_menu_keyboard(gettext_func=lambda text: i18n.gettext(text, locale=user_db.language_code))
    )

