# app/keyboards/inline/admin_verification.py
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def create_verification_keyboard(submission_id: int, user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Tasdiqlash",
        callback_data=f"verify:approve:{submission_id}:{user_id}"
    )
    builder.button(
        text="❌ Rad etish",
        callback_data=f"verify:reject:{submission_id}:{user_id}"
    )
    return builder.as_markup()
