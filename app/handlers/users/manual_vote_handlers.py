# app/handlers/users/manual_vote_handlers.py

from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.config.settings import settings
from app.db.models.users import User
from app.db.models.manual_submission import ManualSubmission
from app.fsm.voting_fsm import VotingStates
from app.keyboards.inline.admin_verification import create_verification_keyboard

router = Router()

@router.message(VotingStates.waiting_for_screenshot, F.photo)
async def handle_screenshot(message: Message, state: FSMContext, session: AsyncSession, bot: Bot, user_db: User):
    """
    Foydalanuvchidan kelgan skrinshotni qabul qiladi, bazaga saqlaydi va adminga yuboradi.
    """
    if not message.photo or not message.from_user:
        await message.answer("Iltimos, faqat rasm (skrinshot) yuboring.")
        return
        
    file_id = message.photo[-1].file_id
    logger.info(f"Foydalanuvchi {message.from_user.id} dan skrinshot qabul qilindi: {file_id}")

    # Yangi talabnomani bazaga saqlaymiz
    new_submission = ManualSubmission(
        user_id=user_db.telegram_id,
        telegram_file_id=file_id
    )
    session.add(new_submission)
    await session.commit() # ID olish uchun commit qilamiz
    
    await state.clear()
    await message.answer(
        "✅ Rahmat! Skrinshotingiz tekshirish uchun adminga yuborildi. "
        "Tasdiqlangan yoki rad etilgani haqida sizga xabar beramiz."
    )

    # Adminga xabar yuborish
    admin_caption = (
        f"📝 Yangi talabnoma!\n\n"
        f"👤 Foydalanuvchi: {message.from_user.full_name}\n"
        f"🆔 ID: `{message.from_user.id}`\n"
        f"🔖 Username: @{message.from_user.username or 'Mavjud emas'}"
    )
    
    # Barcha adminlarga yuboramiz
    for admin_id in settings.ADMIN_IDS:
        try:
            await bot.send_photo(
                chat_id=admin_id,
                photo=file_id,
                caption=admin_caption,
                reply_markup=create_verification_keyboard(new_submission.id, user_db.telegram_id)
            )
        except Exception as e:
            logger.error(f"Adminga ({admin_id}) skrinshot yuborishda xatolik: {e}")

@router.message(VotingStates.waiting_for_screenshot)
async def handle_wrong_content_for_screenshot(message: Message):
    """Agar skrinshot o'rniga boshqa narsa yuborilsa."""
    await message.answer("❌ Iltimos, faqat rasm (skrinshot) yuboring. Agar bekor qilmoqchi bo'lsangiz, /start buyrug'ini bosing.")
