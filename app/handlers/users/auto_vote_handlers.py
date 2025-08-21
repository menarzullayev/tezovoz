# FIX-199
# app/handlers/users/auto_vote_handlers.py

import asyncio
from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.types import Message, BufferedInputFile, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from loguru import logger
import base64
import io
from PIL import Image
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.keyboard import ReplyKeyboardBuilder

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
from app.db.queries.referral_queries import check_and_give_referral_bonus
from app.keyboards.inline.voting_confirmation import create_voting_confirmation_keyboard
from app.keyboards.reply.otp_keyboard import create_otp_keyboard # Yangi import
from datetime import datetime, timedelta

router = Router()

async def animate_loading_message(bot: Bot, chat_id: int, message_id: int, user_locale: str, i18n: I18n):
    animation_frames = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
    base_text = i18n.gettext("⏳ Jarayon bajarilmoqda...", locale=user_locale)
    i = 0
    while True:
        try:
            frame = animation_frames[i % len(animation_frames)]
            await bot.edit_message_text(
                text=f"{base_text} {frame}", chat_id=chat_id, message_id=message_id
            )
            i += 1
            await asyncio.sleep(0.5)
        except (TelegramBadRequest, asyncio.CancelledError):
            break
        except Exception as e:
            logger.error(f"Animatsiyada kutilmagan xatolik: {e}")
            break

@router.message(VotingStates.waiting_for_phone_number, F.contact)
async def handle_phone_number_from_contact(message: Message, state: FSMContext, i18n: I18n, session: AsyncSession, user_db: User, bot: Bot):
    if not message.contact:
        return
    phone_number = message.contact.phone_number.replace("+", "")
    await handle_auto_phone_input(message, state, i18n, session, user_db, bot, phone_number)

@router.message(VotingStates.waiting_for_phone_number, F.text)
async def handle_phone_number_from_text(message: Message, state: FSMContext, i18n: I18n, session: AsyncSession, user_db: User, bot: Bot):
    if not message.text:
        return
    phone_number = message.text.strip().replace("+", "")
    if not phone_number.startswith('998'):
        phone_number = '998' + phone_number.lstrip('0')
    await handle_auto_phone_input(message, state, i18n, session, user_db, bot, phone_number)

async def handle_auto_phone_input(message: Message, state: FSMContext, i18n: I18n, session: AsyncSession, user_db: User, bot: Bot, phone_number: str):
    if not (phone_number.startswith('998') and len(phone_number) == 12 and phone_number.isdigit()):
        await message.answer(i18n.gettext(I18nKeys.PHONE_NUMBER_INVALID, locale=user_db.language_code))
        return
    
    last_vote = await session.scalar(
        select(Vote).where(Vote.user_id == user_db.id).order_by(Vote.voted_at.desc()).limit(1)
    )
    if last_vote and datetime.now(last_vote.voted_at.tzinfo) - last_vote.voted_at < timedelta(hours=24):
        cooldown_end_time = last_vote.voted_at + timedelta(hours=24)
        remaining_time = cooldown_end_time - datetime.now(cooldown_end_time.tzinfo)
        hours, remainder = divmod(remaining_time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        cooldown_message = i18n.gettext(
            I18nKeys.VOTE_COOLDOWN,
            locale=user_db.language_code
        ).format(
            hours=hours,
            minutes=minutes
        )
        await message.answer(cooldown_message)
        return

    await state.update_data(phone_number=phone_number)
    await update_user(session, user_db.telegram_id, phone_number=phone_number)

    await state.set_state(VotingStates.waiting_for_project_id)
    await message.answer(i18n.gettext(I18nKeys.ASK_PROJECT_ID, locale=user_db.language_code))

@router.message(VotingStates.waiting_for_project_id, F.text)
async def handle_project_id_input(message: Message, state: FSMContext, i18n: I18n, user_db: User, bot: Bot):
    if not message.text or not message.text.isdigit():
        await message.answer(i18n.gettext(I18nKeys.PROJECT_ID_INVALID, locale=user_db.language_code))
        return
    
    project_id = int(message.text)
    
    status_message = await message.answer("⏳")
    animation_task = asyncio.create_task(
        animate_loading_message(bot, status_message.chat.id, status_message.message_id, user_db.language_code, i18n)
    )

    captcha_data = None
    try:
        captcha_data = await openbudget_api.get_captcha()
    finally:
        animation_task.cancel()
        with suppress(TelegramBadRequest):
            await bot.delete_message(chat_id=status_message.chat.id, message_id=status_message.message_id)

    if not captcha_data or 'image' not in captcha_data or 'captchaKey' not in captcha_data:
        logger.error(f"CAPTCHA olishda xatolik: {captcha_data}. Qo'lda ovoz berish rejimiga o'tilmoqda.")
        
        # O'rniga qo'lda ovoz berish yo'riqnomasini yuborish
        await state.set_state(VotingStates.waiting_for_screenshot)
        manual_instructions = i18n.gettext(I18nKeys.MANUAL_VOTING_INSTRUCTIONS, locale=user_db.language_code)
        await message.answer(manual_instructions)
        return

    captcha_image_base64 = captcha_data['image']
    if ',' in captcha_image_base64:
        captcha_image_base64 = captcha_image_base64.split(',', 1)[1]

    try:
        image_bytes = base64.b64decode(captcha_image_base64)
        img = Image.open(io.BytesIO(image_bytes))
        output_buffer = io.BytesIO()
        img.save(output_buffer, format="JPEG")
        output_buffer.seek(0)
        photo_file = BufferedInputFile(output_buffer.read(), filename="captcha.jpg")
    except Exception as e:
        logger.error(f"Base64 dekodlashda yoki rasmni qayta ishlashda xatolik: {e}")
        await message.answer(i18n.gettext(I18nKeys.API_ERROR, locale=user_db.language_code))
        await state.clear()
        return
        
    await state.update_data(project_id=project_id, captcha_key=captcha_data['captchaKey'])
    await state.set_state(VotingStates.waiting_for_captcha)

    builder = ReplyKeyboardBuilder()
    builder.button(text=i18n.gettext(I18nButtons.BUTTON_CANCEL, locale=user_db.language_code))
    
    if not message.chat:
        return

    await bot.send_photo(
        chat_id=message.chat.id,
        photo=photo_file,
        caption=i18n.gettext(I18nKeys.ASK_CAPTCHA_RESULT, locale=user_db.language_code),
        reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
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
        elif "Internal server error" in error_message:
             await message.answer(i18n.gettext(I18nKeys.API_SERVER_ERROR, locale=user_db.language_code))
        else:
            # YANGI: CAPTCHA noto'g'ri kiritilganda qayta urinish imkoniyatini berish
            await message.answer(i18n.gettext(I18nKeys.CAPTCHA_INVALID, locale=user_db.language_code))
            return

        await state.clear()
        return

    await state.update_data(otp_key=otp_response['otpKey'])
    await state.set_state(VotingStates.waiting_for_otp)

    await message.answer(
        text=i18n.gettext(I18nKeys.ASK_OTP_CODE, locale=user_db.language_code),
        reply_markup=create_otp_keyboard(gettext_func=lambda text: i18n.gettext(text, locale=user_db.language_code))
    )

@router.message(VotingStates.waiting_for_otp, F.text.in_([
    "🔁 OTP'ni qayta yuborish", "🔁 Отправить OTP повторно", "🔁 Рамзи OTP'ро дубора ирсол кунед"
]))
async def resend_otp(message: Message, state: FSMContext, i18n: I18n, user_db: User):
    """
    OTP kodini qayta yuborish handler'i.
    """
    user_data = await state.get_data()
    phone_number = user_data.get('phone_number')
    captcha_key = user_data.get('captcha_key')
    captcha_result = user_data.get('captcha_result')

    if not phone_number or not captcha_key or not captcha_result:
        await message.answer(i18n.gettext(I18nKeys.ERROR_OCCURRED, locale=user_db.language_code))
        await state.clear()
        return
        
    otp_response = await openbudget_api.send_otp(captcha_key, captcha_result, phone_number)

    if not otp_response or 'otpKey' not in otp_response:
        logger.error(f"OTPni qayta yuborishda xatolik: {otp_response}")
        await message.answer(i18n.gettext(I18nKeys.API_ERROR, locale=user_db.language_code))
        await state.clear()
        return
        
    await state.update_data(otp_key=otp_response['otpKey'])
    await message.answer(i18n.gettext(I18nKeys.ASK_OTP_CODE, locale=user_db.language_code))
    await message.answer(i18n.gettext(I18nKeys.OTP_RESENT_MESSAGE, locale=user_db.language_code))


@router.message(VotingStates.waiting_for_otp, F.text)
async def handle_otp_code(message: Message, state: FSMContext, i18n: I18n, session: AsyncSession, user_db: User, bot: Bot):
    if not message.text or not message.text.isdigit() or len(message.text) != 6:
        await message.answer(i18n.gettext(I18nKeys.OTP_INVALID, locale=user_db.language_code))
        return

    user_data = await state.get_data()
    phone_number = user_data.get('phone_number')
    otp_key = user_data.get('otp_key')
    project_id = user_data.get('project_id')

    if not phone_number or not otp_key or not project_id:
        await message.answer(i18n.gettext(I18nKeys.ERROR_OCCURRED, locale=user_db.language_code))
        await state.clear()
        return
        
    vote_response = await openbudget_api.verify_otp_and_vote(phone_number, message.text, otp_key, project_id)
    
    if not vote_response or 'access_token' not in vote_response:
        logger.error(f"Ovoz berishda xatolik: {vote_response}")
        await message.answer(i18n.gettext(I18nKeys.API_ERROR, locale=user_db.language_code))
        await state.clear()
        return

    vote_amount = 1500
    user_db.balance += vote_amount
    
    new_vote = Vote(user_id=user_db.id, phone_number=phone_number, project_id=project_id)
    session.add(new_vote)
    await session.commit()

    await check_and_give_referral_bonus(session, bot, i18n, user_db)

    success_text = i18n.gettext(I18nKeys.VOTE_SUCCESSFUL, locale=user_db.language_code).format(amount=vote_amount)
    
    await message.answer(
        text=success_text,
        reply_markup=create_main_menu_keyboard(gettext_func=lambda text: i18n.gettext(text, locale=user_db.language_code), is_admin=user_db.is_admin)
    )
    await state.clear()
    if message.from_user:
        logger.info(f"{message.from_user.id} - Ovoz muvaffaqiyatli berildi. Balans: {user_db.balance}")
    else:
        logger.info(f"Ovoz muvaffaqiyatli berildi. Balans: {user_db.balance}")

@router.message(
    StateFilter(VotingStates),
    F.text.in_([
        "❌ Bekor qilish", "❌ Отмена", "❌ Бекор кардан"
    ])
)
async def handle_cancel_vote(message: Message, state: FSMContext, i18n: I18n, user_db: User):
    if not message.from_user:
        return
    logger.info(f"{message.from_user.id} - Jarayonni bekor qildi.")
    await state.clear()
    await message.answer(
        text=i18n.gettext(I18nKeys.CANCEL_ACTION, locale=user_db.language_code),
        reply_markup=create_main_menu_keyboard(gettext_func=lambda text: i18n.gettext(text, locale=user_db.language_code), is_admin=user_db.is_admin)
    )