# app/handlers/admin/messaging.py

import asyncio
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.db.models.users import User
from app.fsm.messaging_fsm import MessagingStates

router = Router()

def create_messaging_confirmation_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Yuborish", callback_data="send_message:confirm")
    builder.button(text="❌ Bekor qilish", callback_data="send_message:cancel")
    return builder.as_markup()

@router.message(Command("send"))
async def start_messaging(message: Message, state: FSMContext):
    """Xabar yuborish jarayonini boshlaydi."""
    await state.set_state(MessagingStates.waiting_for_message)
    await message.answer("📢 Barcha foydalanuvchilarga yuboriladigan xabarni (matn, rasm, video va hokazo) yuboring.")

@router.message(MessagingStates.waiting_for_message, F.content_type.in_({'text', 'photo', 'video', 'animation', 'document', 'voice'}))
async def get_message_content(message: Message, state: FSMContext):
    """Yuboriladigan xabarni qabul qiladi va tasdiqlashni so'raydi."""
    await state.update_data(
        from_chat_id=message.chat.id,
        message_id=message.message_id
    )
    await state.set_state(MessagingStates.waiting_for_confirmation)
    
    await message.copy_to(
        chat_id=message.chat.id,
        reply_markup=create_messaging_confirmation_keyboard()
    )
    await message.answer("✅ Quyidagi xabar barcha foydalanuvchilarga yuboriladi. Tasdiqlaysizmi?")

@router.callback_query(F.data == "send_message:cancel")
async def cancel_messaging(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Xabar yuborish bekor qilindi.")
    await callback.answer()

@router.callback_query(F.data == "send_message:confirm")
async def confirm_and_start_messaging(callback: CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot):
    """Xabarni barcha foydalanuvchilarga yuborishni boshlaydi."""
    data = await state.get_data()
    from_chat_id = data.get("from_chat_id")
    message_id = data.get("message_id")

    if not from_chat_id or not message_id:
        await callback.answer("Xatolik: Yuboriladigan xabar topilmadi.", show_alert=True)
        return

    await state.clear()
    await callback.message.edit_text("🚀 Xabar yuborish boshlandi... Bu biroz vaqt olishi mumkin.")
    
    user_ids = await session.scalars(select(User.telegram_id))
    total_users = 0
    successful_sends = 0
    failed_sends = 0

    for user_id in user_ids:
        total_users += 1
        try:
            await bot.copy_message(chat_id=user_id, from_chat_id=from_chat_id, message_id=message_id)
            successful_sends += 1
        except Exception as e:
            failed_sends += 1
            logger.warning(f"Foydalanuvchiga ({user_id}) xabar yuborishda xatolik: {e}")
        
        # Telegram limitiga tushmaslik uchun
        if total_users % 25 == 0:
            await asyncio.sleep(1)
            
    result_text = (
        f"✅ Xabar yuborish yakunlandi!\n\n"
        f"👥 Jami foydalanuvchilar: {total_users}\n"
        f"👍 Muvaffaqiyatli: {successful_sends}\n"
        f"👎 Xatolik: {failed_sends}"
    )
    await callback.message.answer(result_text)
    await callback.answer()
