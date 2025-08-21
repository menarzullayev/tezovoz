# FIX-180
# app/handlers/users/account.py

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger
import datetime 
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest

from app.db.models.users import User
from app.db.models.votes import Vote
from app.db.models.payment import Payment, PaymentStatusEnum
from app.core.constants.i18n_texts import I18nKeys
from aiogram.utils.i18n import I18n
from app.db.queries.vote_queries import get_user_votes # Yangi import

router = Router()

MIN_WITHDRAWAL_AMOUNT = 10000 

@router.message(F.text.in_([
    "💰 Hisobim", "💰 Мой счёт", "💰 Ҳисоби ман"
]))
async def handle_account_info(message: Message, session: AsyncSession, i18n: I18n, user_db: User):
    """
    "Hisobim" tugmasi bosilganda foydalanuvchiga to'liq ma'lumot va "Pul yechish" tugmasini yuboradi.
    """
    if not message.from_user:
        return
    
    logger.info(f"Foydalanuvchi {user_db.telegram_id} hisob sahifasini so'radi.")

    votes_count_query = select(func.count(Vote.id)).where(Vote.user_id == user_db.id)
    votes_count = await session.scalar(votes_count_query) or 0
    
    total_withdrawn_query = select(func.sum(Payment.amount)).where(
        Payment.user_id == user_db.id,
        Payment.status == PaymentStatusEnum.PAID
    )
    total_withdrawn = await session.scalar(total_withdrawn_query) or 0.0

    registered_date = user_db.created_at.strftime("%d.%m.%Y")
    
    account_info_text = (
        f"👤 **Foydalanuvchi profili**\n\n"
        f"**🆔 ID:** `{user_db.telegram_id}`\n"
        f"**🔖 Username:** @{user_db.username if user_db.username else 'Noma''lum'}\n"
        f"**🗓 Ro'yxatdan o'tgan:** `{registered_date}`\n"
        f"**👑 Admin:** {'Ha' if user_db.is_admin else 'Yo''q'}\n"
        f"**📞 Telefon raqami:** `{user_db.phone_number if user_db.phone_number else 'Kiritilmagan'}`\n\n"
        f"💰 **Balans:** {f'{user_db.balance:,.0f}'.replace(',', ' ')} so'm\n"
        f"💸 **Yechilgan:** {f'{total_withdrawn:,.0f}'.replace(',', ' ')} so'm\n"
        f"🗳 **Jami ovozlar:** {votes_count} ta"
    )

    builder = InlineKeyboardBuilder()
    if user_db.balance >= MIN_WITHDRAWAL_AMOUNT:
        builder.button(
            text=i18n.gettext(I18nKeys.BUTTON_WITHDRAW, locale=user_db.language_code),
            callback_data="withdraw_start"
        )
    
    # Ovozlar tarixi uchun yangi tugma
    if votes_count > 0:
        builder.button(
            text=i18n.gettext(I18nKeys.BUTTON_VOTE_HISTORY, locale=user_db.language_code),
            callback_data="vote_history"
        )
    
    pending_payment_query = select(Payment).where(
        Payment.user_id == user_db.id,
        Payment.status == PaymentStatusEnum.PENDING
    )
    pending_payment = await session.scalar(pending_payment_query)
    if pending_payment:
         account_info_text += f"\n\n⏳ **Pul yechish so'rovi kutmoqda:** {f'{pending_payment.amount:,.0f}'.replace(',', ' ')} so'm"
         builder.button(text=i18n.gettext(I18nKeys.BUTTON_CANCEL, locale=user_db.language_code), callback_data=f"cancel_payment:{pending_payment.id}")

    await message.answer(account_info_text, reply_markup=builder.as_markup(), parse_mode="Markdown")

@router.callback_query(F.data.startswith("cancel_payment:"))
async def handle_cancel_payment(callback: CallbackQuery, session: AsyncSession, i18n: I18n, user_db: User):
    if not callback.data or not callback.message or not isinstance(callback.message, Message):
        await callback.answer(i18n.gettext(I18nKeys.ERROR_OCCURRED, locale=user_db.language_code), show_alert=True)
        return
    
    try:
        _, payment_id_str = callback.data.split(":")
        payment_id = int(payment_id_str)
    except (ValueError, IndexError):
        await callback.answer(i18n.gettext(I18nKeys.ERROR_OCCURRED, locale=user_db.language_code), show_alert=True)
        return
        
    payment = await session.get(Payment, payment_id)
    
    if not payment or payment.user_id != user_db.id or payment.status != PaymentStatusEnum.PENDING:
        await callback.answer(i18n.gettext(I18nKeys.WITHDRAWAL_CANCEL_ERROR, locale=user_db.language_code), show_alert=True)
        return
        
    payment.status = PaymentStatusEnum.CANCELED
    user_db.balance += payment.amount
    await session.commit()
    
    original_text = callback.message.text or ""
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            text=original_text.split('\n\n⏳')[0],
            reply_markup=None
        )
            
    await callback.answer(i18n.gettext(I18nKeys.WITHDRAWAL_CANCELLED_MESSAGE, locale=user_db.language_code), show_alert=True)
    
@router.callback_query(F.data == "vote_history")
async def show_vote_history(callback: CallbackQuery, session: AsyncSession, i18n: I18n, user_db: User):
    """
    Foydalanuvchining ovoz berish tarixini ko'rsatadi.
    """
    if not callback.message or not isinstance(callback.message, Message):
        return

    votes = await get_user_votes(session, user_db.id)
    
    if not votes:
        await callback.answer(i18n.gettext(I18nKeys.NO_VOTES_FOUND, locale=user_db.language_code), show_alert=True)
        return

    history_text = f"🗳 **Sizning ovoz berish tarixingiz:**\n\n"
    for vote in votes:
        vote_time = vote.voted_at.strftime("%d.%m.%Y %H:%M")
        history_text += f"• **Sana:** `{vote_time}`\n"
        history_text += f"• **Loyihaga ID:** `{vote.project_id if vote.project_id else 'Noma''lum'}`\n"
        history_text += f"• **Telefon raqami:** `{vote.phone_number}`\n\n"

    await callback.message.edit_text(
        text=history_text,
        reply_markup=InlineKeyboardBuilder().button(
            text=i18n.gettext(I18nKeys.BUTTON_BACK, locale=user_db.language_code),
            callback_data="account_back"
        ).as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "account_back")
async def back_to_account(callback: CallbackQuery, session: AsyncSession, i18n: I18n, user_db: User):
    """
    Ovoz berish tarixidan hisob sahifasiga qaytaradi.
    """
    if not callback.message:
        return
    await handle_account_info(callback.message, session, i18n, user_db)
    await callback.answer()
