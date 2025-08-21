# app/handlers/admin/verification_handler.py (Yakuniy versiya)

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from loguru import logger

from app.db.models.manual_submission import ManualSubmission, SubmissionStatusEnum
from app.db.models.users import User
from app.db.models.votes import Vote # YANGI IMPORT
from app.db.queries.user_crud_queries import get_user_by_telegram_id
from app.db.queries.referral_queries import check_and_give_referral_bonus # YANGI IMPORT
from aiogram.utils.i18n import I18n # YANGI IMPORT

router = Router()

@router.callback_query(F.data.startswith("verify:"))
async def handle_verification_callback(callback: CallbackQuery, session: AsyncSession, bot: Bot, i18n: I18n):
    """
    Admin skrinshotni tasdiqlash/rad etish tugmasini bosganda ishlaydi.
    """
    # Pylance ogohlantirishini oldini olish uchun tekshiruvlar
    if not callback.data or not callback.message or not callback.from_user:
        return

    try:
        _, action, submission_id_str, user_id_str = callback.data.split(":")
        submission_id = int(submission_id_str)
        user_id = int(user_id_str)
    except (ValueError, IndexError) as e:
        logger.error(f"Callback datani o'qishda xatolik: {callback.data} | {e}")
        await callback.answer("Xatolik yuz berdi!", show_alert=True)
        return

    submission = await session.get(ManualSubmission, submission_id)
    if not submission:
        await callback.answer("Bu talabnoma topilmadi.", show_alert=True)
        return

    if submission.status != SubmissionStatusEnum.PENDING:
        await callback.answer("Bu talabnoma allaqachon tekshirilgan.", show_alert=True)
        return

    target_user = await get_user_by_telegram_id(session, user_id)
    if not target_user:
        await callback.answer("Foydalanuvchi topilmadi.", show_alert=True)
        return

    admin_name = callback.from_user.full_name
    
    # Pylance ogohlantirishini oldini olish uchun tekshiruv
    # Adminga yuborilgan xabar rasm bo'lgani uchun 'caption' bo'lishi kerak
    original_caption = ""
    if isinstance(callback.message, Message) and callback.message.caption:
        original_caption = callback.message.caption

    if action == "approve":
        submission.status = SubmissionStatusEnum.APPROVED
        
        # Qo'lda tasdiqlashni ham "ovoz" deb hisoblaymiz
        new_vote = Vote(user_id=target_user.id, phone_number="manual")
        session.add(new_vote)
        
        reward_amount = 1500
        target_user.balance += reward_amount
        
        await session.commit()
        
        # --- REFERAL BONUSINI TEKSHIRISH ---
        await check_and_give_referral_bonus(session, bot, i18n, target_user)
        # --- YAKUNLANDI ---
        
        if isinstance(callback.message, Message):
            await callback.message.edit_caption(
                caption=original_caption + f"\n\n<b>✅ {admin_name} tomonidan tasdiqlandi</b>",
                reply_markup=None
            )
        
        try:
            await bot.send_message(
                chat_id=user_id,
                text=f"🎉 Tabriklaymiz! Siz yuborgan skrinshot tasdiqlandi.\nHisobingizga <b>{reward_amount} so'm</b> qo'shildi."
            )
        except Exception as e:
            logger.error(f"Foydalanuvchiga ({user_id}) tasdiq xabarini yuborishda xatolik: {e}")
            
        await callback.answer("✅ Tasdiqlandi!", show_alert=False)

    elif action == "reject":
        submission.status = SubmissionStatusEnum.REJECTED
        await session.commit()

        if isinstance(callback.message, Message):
            await callback.message.edit_caption(
                caption=original_caption + f"\n\n<b>❌ {admin_name} tomonidan rad etildi</b>",
                reply_markup=None
            )

        try:
            await bot.send_message(
                chat_id=user_id,
                text=(
                    "😔 Afsuski, siz yuborgan skrinshot admin tomonidan rad etildi.\n"
                    "Iltimos, yo'riqnomaga diqqat bilan amal qilib, qaytadan urinib ko'ring."
                )
            )
        except Exception as e:
            logger.error(f"Foydalanuvchiga ({user_id}) rad etish xabarini yuborishda xatolik: {e}")

        await callback.answer("❌ Rad etildi!", show_alert=False)
