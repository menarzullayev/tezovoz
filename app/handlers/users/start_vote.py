# app/handlers/users/start_vote.py
# FIX-106
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from app.db.models.settings import Settings as SettingsModel
from app.db.models.users import User
from app.fsm.voting_fsm import VotingStates
from app.core.constants.i18n_texts import I18nKeys
from app.core.constants.i18n_buttons import I18nButtons
from aiogram.utils.i18n import I18n

router = Router()

@router.message(F.text.in_([
    "🗣 Ovoz berish", "🗣 Голосовать", "🗣 Овоз додан"
]))
@router.message(Command("vote"))
async def handle_start_vote(message: Message, state: FSMContext, session: AsyncSession, i18n: I18n, user_db: User):
    """
    "Ovoz berish" tugmasi bosilganda, bot rejimini tekshiradi va mos ishni boshlaydi.
    """
    logger.info(f"Debug: 'Ovoz berish' handler'i chaqirildi. User ID: {message.from_user.id if message.from_user else 'Noma\'lum'}")

    # FIX-106: message.from_user obyekti mavjudligini tekshirish
    if not message.from_user:
        logger.warning("Debug: `message.from_user` obyekti topilmadi. Funksiya to'xtatildi.")
        return
        
    logger.info(f"Debug: {message.from_user.id} - Ovoz berish jarayonini boshladi.")
    await state.clear()
    logger.debug("Debug: FSM holati tozalab tashlandi.")

    try:
        mode_setting = await session.scalar(select(SettingsModel).where(SettingsModel.key == "VOTING_MODE"))
        voting_mode = mode_setting.value if mode_setting else "auto"
    except Exception as e:
        logger.error(f"Debug: VOTING_MODE sozlamasini o'qishda xatolik: {e}", exc_info=True)
        voting_mode = "auto" # Xatolik bo'lsa, standart rejimga o'tamiz
        
    logger.debug(f"Debug: Joriy ovoz berish rejimi: {voting_mode}")

    if voting_mode == "manual":
        logger.debug("Debug: Rejim 'manual'. Qo'lda ovoz berish yo'riqnomasi yuboriladi.")
        try:
            link_setting = await session.scalar(select(SettingsModel).where(SettingsModel.key == "MANUAL_VOTING_LINK"))
            if not link_setting or not link_setting.value:
                # FIX-106: Matn i18n orqali olinadi
                text = i18n.gettext(I18nKeys.MANUAL_VOTING_LINK_NOT_SET, locale=user_db.language_code)
                await message.answer(text)
                logger.warning("Debug: MANUAL_VOTING_LINK sozlamasi o'rnatilmagan.")
                return

            await state.set_state(VotingStates.waiting_for_screenshot)
            logger.debug("Debug: FSM holati 'waiting_for_screenshot' ga o'rnatildi.")
            
            # FIX-106: Yo'riqnoma matni i18n orqali olinadi
            instructions = i18n.gettext(I18nKeys.MANUAL_VOTING_INSTRUCTIONS, locale=user_db.language_code).format(
                link=link_setting.value
            )
            await message.answer(instructions, disable_web_page_preview=True)
            logger.debug("Debug: Qo'lda ovoz berish yo'riqnomasi yuborildi.")

        except Exception as e:
            logger.error(f"Debug: Qo'lda ovoz berish jarayonida xatolik yuz berdi: {e}", exc_info=True)
            # FIX-106: Xatolik haqida foydalanuvchiga xabar berish
            await message.answer(i18n.gettext(I18nKeys.ERROR_OCCURRED, locale=user_db.language_code))
            await state.clear()
            return

    else:
        logger.debug("Debug: Rejim 'auto'. Telefon raqam so'raladi.")
        await state.set_state(VotingStates.waiting_for_phone_number)
        logger.debug("Debug: FSM holati 'waiting_for_phone_number' ga o'rnatildi.")
        
        builder = ReplyKeyboardBuilder()
        builder.button(text=i18n.gettext(I18nButtons.BUTTON_SEND_PHONE, locale=user_db.language_code), request_contact=True)
        builder.button(text=i18n.gettext(I18nButtons.BUTTON_CANCEL, locale=user_db.language_code))
        builder.adjust(1)

        await message.answer(
            text=i18n.gettext(I18nKeys.ASK_PHONE_NUMBER, locale=user_db.language_code),
            reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
        )
        logger.debug("Debug: Telefon raqamini so'rash xabari yuborildi.")
    
    logger.debug("Debug: handle_start_vote funksiyasi yakunlandi.")

