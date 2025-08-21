# NEW-181
# app/db/queries/vote_queries.py

from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.db.models.votes import Vote

async def get_user_votes(session: AsyncSession, user_id: int) -> List[Vote]:
    """
    Foydalanuvchining barcha ovozlarini ma'lumotlar bazasidan oladi.

    Args:
        session (AsyncSession): Ma'lumotlar bazasi sessiyasi.
        user_id (int): Foydalanuvchining ID'si.

    Returns:
        List[Vote]: Ovozlar ro'yxati.
    """
    try:
        stmt = select(Vote).where(Vote.user_id == user_id)
        result = await session.execute(stmt)
        votes = result.scalars().all()
        logger.debug(f"Foydalanuvchi {user_id} uchun {len(votes)} ta ovoz topildi.")
        return list(votes)
    except Exception as e:
        logger.error(f"Ovoz berish tarixini olishda xatolik: {e}", exc_info=True)
        return []