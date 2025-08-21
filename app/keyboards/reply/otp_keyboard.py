# NEW-198
# app/keyboards/reply/otp_keyboard.py

from typing import Callable
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from app.core.constants.i18n_buttons import I18nButtons

def create_otp_keyboard(gettext_func: Callable[[str], str]) -> ReplyKeyboardMarkup:
    """
    OTP so'rovlari uchun klaviatura yaratadi.
    """
    builder = ReplyKeyboardBuilder()
    builder.button(text=gettext_func(I18nButtons.BUTTON_RESEND_OTP))
    builder.button(text=gettext_func(I18nButtons.BUTTON_CANCEL))
    builder.adjust(1, 1)

    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
    )


