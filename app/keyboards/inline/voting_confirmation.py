# NEW-188
# app/keyboards/inline/voting_confirmation.py

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def create_voting_confirmation_keyboard() -> InlineKeyboardMarkup:
    """
    Ovoz berish jarayonini tasdiqlash uchun inline tugmalarni yaratadi.
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Tasdiqlash",
        callback_data="confirm_vote"
    )
    builder.button(
        text="❌ Bekor qilish",
        callback_data="cancel_vote"
    )
    return builder.as_markup()