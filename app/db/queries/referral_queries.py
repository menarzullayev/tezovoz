# app/db/queries/referral_queries.py

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from loguru import logger

from app.db.models.users import User
from app.db.models.votes import Vote
from app.db.models.referral import Referral, ReferralStatusEnum
from app.core.constants.i18n_texts import I18nKeys
from aiogram.utils.i18n import I18n

REWARD_AMOUNT = 1000  # Referal uchun mukofot miqdori

async def check_and_give_referral_bonus(
    session: AsyncSession,
    bot: Bot,
    i18n: I18n,
    referred_user: User
):
    """
    Foydalanuvchining birinchi ovozi uchun referal bonusini tekshiradi va beradi.
    """
    try:
        # 1. Foydalanuvchining jami ovozlari sonini tekshiramiz
        votes_count = await session.scalar(
            select(func.count(Vote.id)).where(Vote.user_id == referred_user.id)
        )

        # Agar bu uning birinchi ovozi bo'lsa (yoki manual tasdiqlangan birinchi skrinshoti)
        if votes_count == 1:
            logger.info(f"Foydalanuvchi {referred_user.id} birinchi marta ovoz berdi. Bonus tekshirilmoqda...")
            
            # 2. Uni kim taklif qilganini va bonus to'lanmaganligini tekshiramiz
            referral_record = await session.scalar(
                select(Referral).where(
                    Referral.referred_id == referred_user.id,
                    Referral.status == ReferralStatusEnum.ACTIVE
                )
            )

            if referral_record:
                # 3. Taklif qilgan odamni (referrer) topamiz
                referrer_user = await session.get(User, referral_record.referrer_id)
                if referrer_user:
                    # 4. Bonusni hisoblaymiz va xabar yuboramiz
                    referrer_user.balance += REWARD_AMOUNT
                    referral_record.status = ReferralStatusEnum.PAID # Qayta bonus berilmasligi uchun
                    await session.commit()

                    logger.success(f"Referrer {referrer_user.id} ga {REWARD_AMOUNT} so'm bonus berildi.")
                    
                    # Referrerga xabar yuborish
                    bonus_text = i18n.gettext(
                        I18nKeys.REFERRAL_BONUS_NOTIFICATION,
                        locale=referrer_user.language_code
                    ).format(reward_amount=REWARD_AMOUNT)

                    await bot.send_message(referrer_user.telegram_id, bonus_text)
    except Exception as e:
        logger.error(f"Referal bonusini berishda kutilmagan xatolik: {e}")

