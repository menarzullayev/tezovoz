# NEW-124
# app/keyboards/inline/language_selection.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.config.settings import settings
from aiogram.utils.i18n import gettext as _

def create_language_selection_keyboard() -> InlineKeyboardMarkup:
    """
    Qo'llab-quvvatlanadigan tillar uchun inline klaviatura yaratadi.
    Tugmalar settings.py faylidagi LANGUAGE_CODES_MAPPING lug'atidan dinamik olinadi.
    """
    builder = InlineKeyboardBuilder()

    for lang_code, (lang_name, emoji) in settings.LANGUAGE_CODES_MAPPING.items():
        builder.button(
            text=f"{emoji} {lang_name}",
            callback_data=f"lang:{lang_code}"
        )

    builder.adjust(2)
    return builder.as_markup()