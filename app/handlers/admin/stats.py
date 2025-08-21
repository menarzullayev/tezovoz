# app/handlers/admin/stats.py

import datetime
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.models.users import User
from app.db.models.votes import Vote
from app.db.models.manual_submission import ManualSubmission, SubmissionStatusEnum
from app.db.models.payment import Payment, PaymentStatusEnum

router = Router()

@router.message(Command("stats"))
async def get_bot_statistics(message: Message, session: AsyncSession):
    """
    Botning umumiy statistikasi haqida ma'lumot yuboradi.
    """
    # Umumiy foydalanuvchilar soni
    total_users = await session.scalar(select(func.count(User.id))) or 0

    # Oxirgi 24 soatda qo'shilganlar
    twenty_four_hours_ago = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    new_users_today = await session.scalar(
        select(func.count(User.id)).where(User.created_at >= twenty_four_hours_ago)
    ) or 0

    # Jami berilgan ovozlar (avto + manual)
    total_votes = await session.scalar(select(func.count(Vote.id))) or 0

    # Tekshiruvni kutayotgan skrinshotlar
    pending_screenshots = await session.scalar(
        select(func.count(ManualSubmission.id)).where(ManualSubmission.status == SubmissionStatusEnum.PENDING)
    ) or 0

    # Tekshiruvni kutayotgan pul yechish so'rovlari
    pending_withdrawals = await session.scalar(
        select(func.count(Payment.id)).where(Payment.status == PaymentStatusEnum.PENDING)
    ) or 0

    # Matnni formatlash
    stats_text = (
        f"📊 **Bot Statistikasi**\n\n"
        f"👤 **Foydalanuvchilar:**\n"
        f"   - Umumiy soni: {total_users} ta\n"
        f"   - Oxirgi 24 soatda: +{new_users_today} ta\n\n"
        f"🗳 **Ovozlar:**\n"
        f"   - Jami berilgan ovozlar: {total_votes} ta\n\n"
        f"⏳ **Tekshiruvni kutmoqda:**\n"
        f"   - Skrinshotlar: {pending_screenshots} ta\n"
        f"   - Pul yechish so'rovlari: {pending_withdrawals} ta"
    )

    await message.answer(stats_text, parse_mode="HTML")

