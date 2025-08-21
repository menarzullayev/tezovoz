# NEW-200
# app/keyboards/reply/admin_menu.py

from typing import Callable
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from app.core.constants.i18n_buttons import I18nButtons
from app.core.constants.i18n_texts import I18nKeys

def create_admin_menu_keyboard(gettext_func: Callable[[str], str]) -> ReplyKeyboardMarkup:
    """
    Admin paneli uchun asosiy menyu klaviaturasini yaratadi.
    """
    builder = ReplyKeyboardBuilder()
    
    builder.button(text=gettext_func(I18nButtons.BUTTON_ADMIN_STATS))
    builder.button(text=gettext_func(I18nButtons.BUTTON_ADMIN_MESSAGING))
    builder.button(text=gettext_func(I18nButtons.BUTTON_ADMIN_SETTINGS))
    builder.button(text=gettext_func(I18nButtons.BUTTON_ADMIN_USER_MANAGEMENT)) # Yangi tugma
    builder.button(text=gettext_func(I18nButtons.BUTTON_MAIN_MENU))

    builder.adjust(2, 2, 1)

    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder=gettext_func(I18nKeys.ADMIN_PANEL_MESSAGE)
    )