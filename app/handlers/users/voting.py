# FIX-153 (Yakuniy versiya, DEBUG kodlari bilan)
# app/handlers/users/voting.py

import asyncio
import datetime
from typing import Any, Optional
from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, ReplyKeyboardMarkup, BufferedInputFile
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
import base64
import io

from app.config.settings import settings
from app.db.queries.user_crud_queries import update_user
from app.db.models.users import User
from app.db.models.votes import Vote
from app.fsm.voting_fsm import VotingStates
from app.keyboards.reply.main_menu import create_main_menu_keyboard
from app.core.constants.i18n_texts import I18nKeys
from app.core.constants.i18n_buttons import I18nButtons
from app.utils.api_client import openbudget_api
from aiogram.utils.i18n import I18n

router = Router()

@router.message(F.text.in_([
    "🗣 Ovoz berish", "🗣 Голосовать", "🗣 Овоз додан"
]))
@router.message(Command("vote"))
async def handle_start_vote(message: Message, state: FSMContext, i18n: I18n, user_db: User):
    logger.info(f"{message.from_user.id} - Ovoz berish jarayonini boshladi.")
    await state.set_state(VotingStates.waiting_for_phone_number)
    
    reply_keyboard = ReplyKeyboardMarkup(keyboard=[
        [
            {'text': i18n.gettext(I18nButtons.BUTTON_SEND_PHONE, locale=user_db.language_code), 'request_contact': True}
        ],
        [
            {'text': i18n.gettext(I18nButtons.BUTTON_CANCEL, locale=user_db.language_code)}
        ]
    ], resize_keyboard=True, one_time_keyboard=True)

    await message.answer(
        text=i18n.gettext(I18nKeys.ASK_PHONE_NUMBER, locale=user_db.language_code),
        reply_markup=reply_keyboard
    )

@router.message(VotingStates.waiting_for_phone_number, F.contact)
async def handle_phone_number_from_contact(message: Message, state: FSMContext, i18n: I18n, session: AsyncSession, user_db: User, bot: Bot):
    phone_number = message.contact.phone_number.replace("+", "")
    await handle_phone_number_input(message, state, i18n, session, user_db, bot, phone_number)

@router.message(VotingStates.waiting_for_phone_number, F.text)
async def handle_phone_number_from_text(message: Message, state: FSMContext, i18n: I18n, session: AsyncSession, user_db: User, bot: Bot):
    phone_number = message.text.strip().replace("+", "")
    if not phone_number.startswith('998'):
        phone_number = '998' + phone_number.lstrip('0')
    await handle_phone_number_input(message, state, i18n, session, user_db, bot, phone_number)

async def handle_phone_number_input(message: Message, state: FSMContext, i18n: I18n, session: AsyncSession, user_db: User, bot: Bot, phone_number: str):
    if not (phone_number.startswith('998') and len(phone_number) == 12 and phone_number.isdigit()):
        await message.answer(i18n.gettext(I18nKeys.PHONE_NUMBER_INVALID, locale=user_db.language_code))
        return

    await update_user(session, user_db.telegram_id, phone_number=phone_number)

    captcha_data = await openbudget_api.get_captcha()
    if not captcha_data or 'image' not in captcha_data or 'captchaKey' not in captcha_data:
        logger.error(f"CAPTCHA olishda xatolik: {captcha_data}")
        await message.answer(i18n.gettext(I18nKeys.API_ERROR, locale=user_db.language_code))
        await state.clear()
        return

    captcha_image_base64 = captcha_data['image']
    captcha_key = captcha_data['captchaKey']

    # --- YECHIM va DEBUG KODLARI ---
    logger.debug(f"Xom base64 kodining boshi: {captcha_image_base64[:60]}")
    if ',' in captcha_image_base64:
        # Verguldan keyingi qismini olamiz, bu toza base64 kodi bo'ladi
        captcha_image_base64 = captcha_image_base64.split(',', 1)[1]
        logger.debug("Base64 kodi tozalandi.")
    
    try:
        image_bytes = base64.b64decode(captcha_image_base64)
        photo_file = BufferedInputFile(image_bytes, filename="captcha.jpg")
        logger.debug("Rasm baytlari muvaffaqiyatli Telegramga yuborish uchun tayyorlandi.")
    except Exception as e:
        logger.error(f"Base64 dekodlashda yoki fayl yaratishda xatolik: {e}")
        await message.answer(i18n.gettext(I18nKeys.API_ERROR, locale=user_db.language_code))
        await state.clear()
        return
        
    await state.update_data(phone_number=phone_number, captcha_key=captcha_key)
    await state.set_state(VotingStates.waiting_for_captcha)

    await bot.send_photo(
        chat_id=message.chat.id,
        photo=photo_file,
        caption=i18n.gettext(I18nKeys.ASK_CAPTCHA_RESULT, locale=user_db.language_code),
        reply_markup=ReplyKeyboardMarkup(keyboard=[
            [{'text': i18n.gettext(I18nButtons.BUTTON_CANCEL, locale=user_db.language_code)}]
        ], resize_keyboard=True, one_time_keyboard=True)
    )

@router.message(VotingStates.waiting_for_captcha, F.text)
async def handle_captcha_result(message: Message, state: FSMContext, i18n: I18n, user_db: User, bot: Bot):
    if not message.text or not message.text.isdigit():
        await message.answer(i18n.gettext(I18nKeys.CAPTCHA_INVALID, locale=user_db.language_code))
        return

    user_data = await state.get_data()
    phone_number = user_data.get('phone_number')
    captcha_key = user_data.get('captcha_key')

    if not phone_number or not captcha_key:
        await message.answer(i18n.gettext(I18nKeys.ERROR_OCCURRED, locale=user_db.language_code))
        await state.clear()
        return

    otp_response = await openbudget_api.send_otp(captcha_key, int(message.text), phone_number)
    
    if not otp_response or 'otpKey' not in otp_response:
        logger.error(f"OTP yuborishda xatolik: {otp_response}")
        error_message = otp_response.get("message", "") if isinstance(otp_response, dict) else ""
        if "used" in error_message:
             await message.answer(i18n.gettext(I18nKeys.PHONE_ALREADY_USED, locale=user_db.language_code))
        else:
            await message.answer(i18n.gettext(I18nKeys.API_ERROR, locale=user_db.language_code))
        await state.clear()
        return

    await state.update_data(otp_key=otp_response['otpKey'])
    await state.set_state(VotingStates.waiting_for_otp)

    await message.answer(
        text=i18n.gettext(I18nKeys.ASK_OTP_CODE, locale=user_db.language_code),
        reply_markup=ReplyKeyboardMarkup(keyboard=[
            [{'text': i18n.gettext(I18nButtons.BUTTON_CANCEL, locale=user_db.language_code)}]
        ], resize_keyboard=True, one_time_keyboard=True)
    )

@router.message(VotingStates.waiting_for_otp, F.text)
async def handle_otp_code(message: Message, state: FSMContext, i18n: I18n, session: AsyncSession, user_db: User):
    if not message.text or not message.text.isdigit() or len(message.text) != 6:
        await message.answer(i18n.gettext(I18nKeys.OTP_INVALID, locale=user_db.language_code))
        return

    user_data = await state.get_data()
    phone_number = user_data.get('phone_number')
    otp_key = user_data.get('otp_key')

    if not phone_number or not otp_key:
        await message.answer(i18n.gettext(I18nKeys.ERROR_OCCURRED, locale=user_db.language_code))
        await state.clear()
        return

    vote_response = await openbudget_api.verify_otp_and_vote(phone_number, message.text, otp_key)
    
    if not vote_response or 'access_token' not in vote_response:
        logger.error(f"Ovoz berishda xatolik: {vote_response}")
        await message.answer(i18n.gettext(I18nKeys.API_ERROR, locale=user_db.language_code))
        await state.clear()
        return

    vote_amount = 1500
    user_db.balance += vote_amount
    
    new_vote = Vote(user_id=user_db.id, phone_number=phone_number, project_id=settings.OPENBUDGET_PROJECT_ID)
    session.add(new_vote)
    await session.commit()

    success_text = i18n.gettext(I18nKeys.VOTE_SUCCESSFUL, locale=user_db.language_code).format(amount=vote_amount)
    
    await message.answer(
        text=success_text,
        reply_markup=create_main_menu_keyboard(gettext_func=lambda text: i18n.gettext(text, locale=user_db.language_code), is_admin=user_db.is_admin)
    )
    await state.clear()
    logger.info(f"{message.from_user.id} - Ovoz muvaffaqiyatli berildi. Balans: {user_db.balance}")

@router.message(
    StateFilter(VotingStates),
    F.text.in_([
        "❌ Bekor qilish", "❌ Отмена", "❌ Бекор кардан"
    ])
)
async def handle_cancel_vote(message: Message, state: FSMContext, i18n: I18n, user_db: User):
    logger.info(f"{message.from_user.id} - Ovoz berish jarayonini bekor qildi.")
    await state.clear()
    await message.answer(
        text=i18n.gettext(I18nKeys.CANCEL_ACTION, locale=user_db.language_code),
        reply_markup=create_main_menu_keyboard(gettext_func=lambda text: i18n.gettext(text, locale=user_db.language_code), is_admin=user_db.is_admin)
    )