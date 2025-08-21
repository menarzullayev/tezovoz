# FIX-169
# app/handlers/users/referral.py

from aiogram import Router, F, Bot
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from loguru import logger

from app.db.models.users import User
from app.db.models.referral import Referral
from app.core.constants.i18n_texts import I18nKeys
from aiogram.utils.i18n import I18n

router = Router()

@router.message(F.text.in_([
    "🔗 Referal", "🔗 Рефералы", "🔗 Реферал"
]))
async def handle_referral_info(message: Message, session: AsyncSession, i18n: I18n, user_db: User, bot: Bot):
    """
    "Referal" tugmasi bosilganda foydalanuvchiga uning shaxsiy havolasi va
    taklif qilgan do'stlari soni haqida ma'lumot yuboradi.
    """
    if not message.from_user:
        return

    logger.info(f"Foydalanuvchi {user_db.telegram_id} referal tizimi haqida ma'lumot so'radi.")

    # Botning username'ini olamiz
    bot_info = await bot.get_me()
    bot_username = bot_info.username

    # Referal havolasini yaratamiz
    referral_link = f"https://t.me/{bot_username}?start=ref{user_db.id}"


    # Foydalanuvchi taklif qilgan do'stlar sonini sanaymiz
    referrals_count_query = select(func.count(Referral.id)).where(Referral.referrer_id == user_db.id)
    referrals_count = await session.scalar(referrals_count_query)

    # Mukofot miqdorini (hozircha statik, keyinchalik sozlamalardan olish mumkin)
    reward_amount = 1000 # Misol uchun

    # Tarjima matnini olamiz va formatlaymiz
    referral_info_text = i18n.gettext(
        I18nKeys.REFERRAL_INFO_MESSAGE,
        locale=user_db.language_code
    ).format(
        reward_amount=f"{reward_amount:,.0f}".replace(",", " "),
        referral_link=referral_link,
        referral_count=referrals_count,
        amount=f"{reward_amount:,.0f}".replace(",", " "),
        link=referral_link,  # FIX: 'link' kaliti qo'shildi
    )

    await message.answer(referral_info_text, disable_web_page_preview=True)

