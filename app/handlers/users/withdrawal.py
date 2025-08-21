# app/handlers/users/withdrawal.py

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.config.settings import settings
from app.db.models.users import User
from app.db.models.payment import Payment, PaymentStatusEnum
from app.fsm.withdrawal_fsm import WithdrawalStates
from app.core.constants.i18n_texts import I18nKeys
from aiogram.utils.i18n import I18n
# Admin uchun alohida tugmalar kerak bo'ladi, uni keyingi qadamda yaratamiz
from app.keyboards.inline.admin_payment_verification import create_payment_verification_keyboard # YANGI IMPORT

# Bu qiymatni account.py dagi bilan bir xil saqlang
MIN_WITHDRAWAL_AMOUNT = 10000

router = Router()

@router.callback_query(F.data == "withdraw_start")
async def start_withdrawal(callback: CallbackQuery, state: FSMContext, i18n: I18n, user_db: User):
    """Pul yechish jarayonini boshlaydi."""
    if not callback.message:
        return

    if user_db.balance < MIN_WITHDRAWAL_AMOUNT:
        await callback.answer(
            i18n.gettext("withdraw-min-amount-error", locale=user_db.language_code).format(min_amount=MIN_WITHDRAWAL_AMOUNT),
            show_alert=True
        )
        return
    
    await state.set_state(WithdrawalStates.waiting_for_card_number)
    await callback.message.answer(i18n.gettext("ask-card-number", locale=user_db.language_code))
    await callback.answer()

@router.message(WithdrawalStates.waiting_for_card_number, F.text)
async def process_card_number(message: Message, state: FSMContext, i18n: I18n, user_db: User):
    """Karta raqamini qabul qiladi va summani so'raydi."""
    if not message.text or not (message.text.isdigit() and len(message.text) == 16):
        await message.answer(i18n.gettext("invalid-card-number", locale=user_db.language_code))
        return

    await state.update_data(card_number=message.text)
    await state.set_state(WithdrawalStates.waiting_for_amount)
    await message.answer(i18n.gettext("ask-amount", locale=user_db.language_code))


@router.message(WithdrawalStates.waiting_for_amount, F.text)
async def process_amount(message: Message, state: FSMContext, session: AsyncSession, i18n: I18n, user_db: User, bot: Bot):
    """Summani qabul qiladi, so'rovni bazaga saqlaydi va adminga yuboradi."""
    if not message.text or not message.text.replace('.', '', 1).isdigit():
        await message.answer(i18n.gettext("invalid-amount", locale=user_db.language_code))
        return

    try:
        amount = float(message.text)
    except ValueError:
        await message.answer(i18n.gettext("invalid-amount", locale=user_db.language_code))
        return
        
    if amount < MIN_WITHDRAWAL_AMOUNT:
        await message.answer(
            i18n.gettext("withdraw-min-amount-error", locale=user_db.language_code).format(min_amount=MIN_WITHDRAWAL_AMOUNT)
        )
        return
    
    if amount > user_db.balance:
        await message.answer(
            i18n.gettext("insufficient-funds", locale=user_db.language_code).format(balance=f"{user_db.balance:,.0f}".replace(",", " "))
        )
        return

    user_data = await state.get_data()
    card_number = user_data.get("card_number")

    new_payment = Payment(
        user_id=user_db.id,
        amount=amount,
        card_number=card_number,
        status=PaymentStatusEnum.PENDING
    )
    session.add(new_payment)
    await session.commit()

    await state.clear()
    await message.answer(i18n.gettext("withdrawal-request-sent", locale=user_db.language_code))

    admin_text = (
        f"💸 Yangi pul yechish so'rovi!\n\n"
        f"👤 Foydalanuvchi: {user_db.first_name} (`{user_db.telegram_id}`)\n"
        f"💳 Karta: `{card_number}`\n"
        f"💰 Summa: **{amount:,.0f} so'm**".replace(",", " ")
    )
    
    for admin_id in settings.ADMIN_IDS:
        try:
            # --- YECHIM: Tugmalarni ham birga yuboramiz ---
            await bot.send_message(
                admin_id, 
                admin_text,
                reply_markup=create_payment_verification_keyboard(new_payment.id, user_db.id)
            )
        except Exception as e:
            logger.error(f"Adminga ({admin_id}) pul yechish so'rovi haqida yuborishda xatolik: {e}")




