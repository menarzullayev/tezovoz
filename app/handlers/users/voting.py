# FIX-153
# app/handlers/users/voting.py

import asyncio
import datetime
from typing import Any, Optional
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, ReplyKeyboardMarkup, BufferedInputFile
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
import base64
import io

from app.config.settings import settings
from app.db.queries.user_crud_queries import get_user_by_telegram_id, update_user
from app.db.models.users import User
from app.db.models.sessions import VotingSession
from app.db.models.votes import Vote
from app.db.models.enums import UserStatusEnum
from app.fsm.voting_fsm import VotingStates
from app.keyboards.reply.main_menu import create_main_menu_keyboard
from app.core.constants.i18n_texts import I18nKeys
from app.core.constants.i18n_buttons import I18nButtons
from app.utils.api_client import openbudget_api
from app.utils.helpers import retry_on_exception
from aiogram.utils.i18n import gettext as _
# from app.utils.captcha_utils import get_captcha_image_from_browser # Endi bu kerak emas

router = Router()

@router.message(F.text == "🗣 Ovoz berish")
@router.message(Command("vote"))
async def handle_start_vote(message: Message, state: FSMContext, i18n: Any, user_db: User, bot: Bot):
    """
    'Ovoz berish' tugmasi bosilganda yoki /vote buyrug'i yuborilganda ishga tushadi.
    """
    logger.info(f"{message.from_user.id} - Ovoz berish jarayonini boshladi.")
    await state.set_state(VotingStates.waiting_for_phone_number)
    
    reply_keyboard = ReplyKeyboardMarkup(keyboard=[
        [
            {'text': i18n.gettext(I18nButtons.BUTTON_SEND_PHONE), 'request_contact': True}
        ],
        [
            {'text': i18n.gettext(I18nButtons.BUTTON_CANCEL)}
        ]
    ], resize_keyboard=True, one_time_keyboard=True)

    await message.answer(
        text=i18n.gettext(I18nKeys.ASK_PHONE_NUMBER),
        reply_markup=reply_keyboard
    )

@router.message(VotingStates.waiting_for_phone_number, F.contact)
async def handle_phone_number_from_contact(message: Message, state: FSMContext, i18n: Any, session: AsyncSession, user_db: User, bot: Bot):
    """
    Foydalanuvchi kontakt orqali telefon raqamini yuborganda.
    """
    phone_number = message.contact.phone_number
    if not phone_number.startswith('+998'):
        phone_number = '+998' + phone_number.lstrip('0')

    await handle_phone_number_input(message, state, i18n, session, user_db, bot, phone_number)

@router.message(VotingStates.waiting_for_phone_number, F.text)
async def handle_phone_number_from_text(message: Message, state: FSMContext, i18n: Any, session: AsyncSession, user_db: User, bot: Bot):
    """
    Foydalanuvchi matn orqali telefon raqamini yuborganda.
    """
    phone_number = message.text.strip()
    if phone_number.startswith('+'):
        phone_number = phone_number.lstrip('+')
    if not phone_number.startswith('998'):
        phone_number = '998' + phone_number.lstrip('0')

    await handle_phone_number_input(message, state, i18n, session, user_db, bot, phone_number)


async def handle_phone_number_input(message: Message, state: FSMContext, i18n: Any, session: AsyncSession, user_db: User, bot: Bot, phone_number: str):
    """
    Telefon raqamini tekshiradi va CAPTCHA so'rovini yuboradi.
    """
    if not (phone_number.startswith('998') and len(phone_number) == 12):
        await message.answer(i18n.gettext(I18nKeys.PHONE_NUMBER_INVALID))
        return

    user_db.phone_number = phone_number
    await session.commit()

    captcha_data = await openbudget_api.get_captcha()
    if not captcha_data or 'image' not in captcha_data or 'captchaKey' not in captcha_data:
        logger.error(f"CAPTCHA olishda xatolik: {captcha_data}")
        await message.answer(i18n.gettext(I18nKeys.API_ERROR))
        await state.clear()
        return

    captcha_image_base64 = captcha_data['image']
    captcha_key = captcha_data['captchaKey']

    image_bytes = base64.b64decode(captcha_image_base64)
    photo_file = BufferedInputFile(io.BytesIO(image_bytes).getvalue(), filename="captcha.jpg")

    await state.update_data(phone_number=phone_number, captcha_key=captcha_key)
    await state.set_state(VotingStates.waiting_for_captcha)

    await bot.send_photo(
        chat_id=message.chat.id,
        photo=photo_file,
        caption=i18n.gettext(I18nKeys.ASK_CAPTCHA_RESULT),
        reply_markup=ReplyKeyboardMarkup(keyboard=[
            [{'text': i18n.gettext(I18nButtons.BUTTON_CANCEL)}]
        ], resize_keyboard=True, one_time_keyboard=True)
    )

@router.message(VotingStates.waiting_for_captcha, F.text)
async def handle_captcha_result(message: Message, state: FSMContext, i18n: Any, session: AsyncSession, user_db: User, bot: Bot):
    """
    CAPTCHA javobini qabul qiladi va OTP yuborishni so'raydi.
    """
    captcha_result = message.text.strip()
    if not captcha_result.isdigit():
        await message.answer(i18n.gettext(I18nKeys.CAPTCHA_INVALID))
        return

    user_data = await state.get_data()
    phone_number = user_data.get('phone_number')
    captcha_key = user_data.get('captcha_key')

    if not phone_number or not captcha_key:
        await message.answer(i18n.gettext(I18nKeys.ERROR_OCCURRED))
        await state.clear()
        return

    # OTP yuborish
    # captcha_result string o'rniga integer qilib yuborilmoqda
    otp_response = await openbudget_api.send_otp(captcha_key, int(captcha_result), phone_number)
    if not otp_response or 'otpKey' not in otp_response:
        logger.error(f"OTP yuborishda xatolik: {otp_response}")
        if otp_response and 'detail' in otp_response and 'used' in otp_response['detail']:
            await message.answer(i18n.gettext(I18nKeys.PHONE_ALREADY_USED))
        else:
            await message.answer(i18n.gettext(I18nKeys.API_ERROR))
        await state.clear()
        return

    otp_key = otp_response['otpKey']
    
    voting_session = await session.get(VotingSession, user_db.id)
    if voting_session:
        voting_session.phone_number = phone_number
        voting_session.captcha_key = captcha_key
        voting_session.otp_key = otp_key
        voting_session.expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=3)
    else:
        voting_session = VotingSession(
            user_id=user_db.id,
            phone_number=phone_number,
            captcha_key=captcha_key,
            otp_key=otp_key,
            expires_at=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=3)
        )
        session.add(voting_session)
    await session.commit()

    await state.update_data(otp_key=otp_key)
    await state.set_state(VotingStates.waiting_for_otp)

    await message.answer(
        text=i18n.gettext(I18nKeys.ASK_OTP_CODE),
        reply_markup=ReplyKeyboardMarkup(keyboard=[
            [{'text': i18n.gettext(I18nButtons.BUTTON_CANCEL)}]
        ], resize_keyboard=True, one_time_keyboard=True)
    )

@router.message(VotingStates.waiting_for_otp, F.text)
async def handle_otp_code(message: Message, state: FSMContext, i18n: Any, session: AsyncSession, user_db: User, bot: Bot):
    """
    OTP kodini qabul qiladi va ovozni tasdiqlaydi.
    """
    otp_code = message.text.strip()
    if not otp_code.isdigit() or len(otp_code) != 6:
        await message.answer(i18n.gettext(I18nKeys.OTP_INVALID))
        return

    user_data = await state.get_data()
    phone_number = user_data.get('phone_number')
    otp_key = user_data.get('otp_key')

    if not phone_number or not otp_key:
        await message.answer(i18n.gettext(I18nKeys.ERROR_OCCURRED))
        await state.clear()
        return

    vote_response = await openbudget_api.verify_otp_and_vote(phone_number, otp_code, otp_key)
    
    if not vote_response or 'access_token' not in vote_response:
        logger.error(f"Ovoz berishda xatolik: {vote_response}")
        await message.answer(i18n.gettext(I18nKeys.API_ERROR))
        await state.clear()
        return

    vote_amount = 1500
    user_db.balance += vote_amount
    await session.commit()

    new_vote = Vote(
        user_id=user_db.id,
        phone_number=phone_number,
        project_id=settings.OPENBUDGET_PROJECT_ID
    )
    session.add(new_vote)
    await session.commit()

    await message.answer(
        text=i18n.gettext(I18nKeys.VOTE_SUCCESSFUL, amount=vote_amount),
        reply_markup=create_main_menu_keyboard(i18n=i18n, is_admin=user_db.is_admin)
    )
    await state.clear()
    logger.info(f"{message.from_user.id} - Ovoz muvaffaqiyatli berildi. Balans: {user_db.balance}")

@router.message(F.text == I18nButtons.BUTTON_CANCEL, VotingStates.waiting_for_phone_number)
@router.message(F.text == I18nButtons.BUTTON_CANCEL, VotingStates.waiting_for_captcha)
@router.message(F.text == I18nButtons.BUTTON_CANCEL, VotingStates.waiting_for_otp)
async def handle_cancel_vote(message: Message, state: FSMContext, i18n: Any, user_db: User):
    """
    Ovoz berish jarayonini bekor qiladi.
    """
    logger.info(f"{message.from_user.id} - Ovoz berish jarayonini bekor qildi.")
    await state.clear()
    await message.answer(
        text=i18n.gettext(I18nKeys.CANCEL_ACTION),
        reply_markup=create_main_menu_keyboard(i18n=i18n, is_admin=user_db.is_admin)
    )
