# FIX-134
# app/keyboards/reply/main_menu.py

from typing import Any, Callable
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from app.core.constants.i18n_buttons import I18nButtons
from app.core.constants.i18n_texts import I18nKeys

# gettext_func parametrini to'g'ri chaqiriluvchi funksiya deb belgilaymiz
def create_main_menu_keyboard(
    gettext_func: Callable[[str], str], 
    is_admin: bool = False
) -> ReplyKeyboardMarkup:
    """
    Botning asosiy menyu klaviaturasini yaratadi.
    :param gettext_func: Tarjima uchun funksiya (masalan, gettext).
    :param is_admin: Agar True bo'lsa, admin paneli tugmasi qo'shiladi.
    :return: ReplyKeyboardMarkup
    """
    builder = ReplyKeyboardBuilder()
    
    # Asosiy tugmalar
    builder.button(text=gettext_func(I18nButtons.BUTTON_START_VOTE))
    builder.button(text=gettext_func(I18nButtons.BUTTON_ACCOUNT))
    builder.button(text=gettext_func(I18nButtons.BUTTON_REFERRAL))
    builder.button(text=gettext_func(I18nButtons.BUTTON_HELP))
    
    if is_admin:
        builder.button(text=gettext_func(I18nButtons.BUTTON_ADMIN_PANEL))

    builder.adjust(2, 2)

    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder=gettext_func(I18nKeys.MAIN_MENU_MESSAGE)
    )