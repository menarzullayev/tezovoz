# app/handlers/admin/payment_verification.py

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from app.db.models.payment import Payment, PaymentStatusEnum
from app.db.models.users import User
from app.keyboards.inline.admin_payment_verification import create_payment_verification_keyboard
from app.core.constants.i18n_texts import I18nKeys
from aiogram.utils.i18n import I18n

router = Router()

@router.message(Command("pending_payments"))
async def list_pending_payments(message: Message, session: AsyncSession, bot: Bot):
    """
    Tekshiruvni kutayotgan barcha pul yechish so'rovlarini adminga yuboradi.
    """
    pending_payments = await session.scalars(
        select(Payment).where(Payment.status == PaymentStatusEnum.PENDING).options(
            # User ma'lumotlarini ham birga olish uchun
        )
    )
    
    payments = pending_payments.all()

    if not payments:
        await message.answer("✅ Tekshiruvni kutayotgan pul yechish so'rovlari mavjud emas.")
        return

    for payment in payments:
        user = await session.get(User, payment.user_id)
        if not user:
            continue

        admin_text = (
            f"💸 Yangi pul yechish so'rovi!\n\n"
            f"👤 Foydalanuvchi: {user.first_name} (`{user.telegram_id}`)\n"
            f"💳 Karta: `{payment.card_number}`\n"
            f"💰 Summa: **{payment.amount:,.0f} so'm**".replace(",", " ")
        )
        await bot.send_message(
            chat_id=message.chat.id,
            text=admin_text,
            reply_markup=create_payment_verification_keyboard(payment.id, user.id)
        )

@router.callback_query(F.data.startswith("payment:"))
async def handle_payment_verification(callback: CallbackQuery, session: AsyncSession, bot: Bot, i18n: I18n):
    if not callback.data or not callback.message or not callback.from_user:
        return

    try:
        _, action, payment_id_str, user_id_str = callback.data.split(":")
        payment_id = int(payment_id_str)
        user_id = int(user_id_str)
    except (ValueError, IndexError):
        await callback.answer("Xatolik!", show_alert=True)
        return

    payment = await session.get(Payment, payment_id)
    if not payment:
        await callback.answer("Bu so'rov topilmadi.", show_alert=True)
        return

    if payment.status != PaymentStatusEnum.PENDING:
        await callback.answer("Bu so'rov allaqachon tekshirilgan.", show_alert=True)
        return

    target_user = await session.get(User, user_id)
    if not target_user:
        await callback.answer("Foydalanuvchi topilmadi.", show_alert=True)
        return
        
    admin_name = callback.from_user.full_name
    original_text = callback.message.text or ""

    if action == "approve":
        # Foydalanuvchi balansidan pulni ayiramiz
        if target_user.balance < payment.amount:
            await callback.answer(f"Diqqat! Foydalanuvchi balansida mablag' yetarli emas ({target_user.balance} so'm).", show_alert=True)
            return
            
        target_user.balance -= payment.amount
        payment.status = PaymentStatusEnum.PAID
        
        await session.commit()
        
        await callback.message.edit_text(
            text=original_text + f"\n\n<b>✅ {admin_name} tomonidan tasdiqlandi</b>",
            reply_markup=None
        )
        
        try:
            notification_text = i18n.gettext(
                "payment-approved-user-notification", locale=target_user.language_code
            ).format(amount=payment.amount)
            await bot.send_message(target_user.telegram_id, notification_text)
        except Exception as e:
            logger.error(f"Foydalanuvchiga ({target_user.telegram_id}) tasdiq xabarini yuborishda xatolik: {e}")
            
        await callback.answer("✅ Tasdiqlandi!", show_alert=False)

    elif action == "reject":
        payment.status = PaymentStatusEnum.REJECTED
        await session.commit()

        await callback.message.edit_text(
            text=original_text + f"\n\n<b>❌ {admin_name} tomonidan rad etildi</b>",
            reply_markup=None
        )

        try:
            notification_text = i18n.gettext(
                "payment-rejected-user-notification", locale=target_user.language_code
            ).format(amount=payment.amount)
            await bot.send_message(target_user.telegram_id, notification_text)
        except Exception as e:
            logger.error(f"Foydalanuvchiga ({target_user.telegram_id}) rad etish xabarini yuborishda xatolik: {e}")

        await callback.answer("❌ Rad etildi!", show_alert=False)
