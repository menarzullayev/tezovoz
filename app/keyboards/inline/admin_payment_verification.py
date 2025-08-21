# app/keyboards/inline/admin_payment_verification.py
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def create_payment_verification_keyboard(payment_id: int, user_id: int) -> InlineKeyboardMarkup:
    """Admin uchun pul yechish so'rovini tasdiqlash/rad etish tugmalarini yaratadi."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Tasdiqlash",
        callback_data=f"payment:approve:{payment_id}:{user_id}"
    )
    builder.button(
        text="❌ Rad etish",
        callback_data=f"payment:reject:{payment_id}:{user_id}"
    )
    return builder.as_markup()
