# NEW-119
# app/db/queries/user_crud_queries.py

from typing import Any, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.db.models.users import User
from app.db.models.enums import UserStatusEnum

async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> Optional[User]:
    """
    Telegram ID orqali foydalanuvchini ma'lumotlar bazasidan oladi.

    Args:
        session (AsyncSession): Ma'lumotlar bazasi sessiyasi.
        telegram_id (int): Foydalanuvchining Telegram ID'si.

    Returns:
        Optional[User]: Agar foydalanuvchi topilsa, User obyekti, aks holda None.
    """
    try:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        logger.debug(f"Foydalanuvchi {telegram_id} topildi: {user is not None}")
        return user
    except Exception as e:
        logger.error(f"Foydalanuvchini Telegram ID orqali olishda xatolik: {e}", exc_info=True)
        return None

async def add_user(
    session: AsyncSession,
    telegram_id: int,
    first_name: str,
    last_name: Optional[str] = None,
    username: Optional[str] = None,
    language_code: str = "uz",
    user_status: UserStatusEnum = UserStatusEnum.ACTIVE
) -> User:
    """
    Yangi foydalanuvchini ma'lumotlar bazasiga qo'shadi.

    Args:
        session (AsyncSession): Ma'lumotlar bazasi sessiyasi.
        telegram_id (int): Foydalanuvchining Telegram ID'si.
        first_name (str): Foydalanuvchining ismi.
        last_name (Optional[str]): Foydalanuvchining familiyasi.
        username (Optional[str]): Foydalanuvchining username'i.
        language_code (str): Foydalanuvchining tanlagan tili.
        user_status (UserStatusEnum): Foydalanuvchining holati.

    Returns:
        User: Yaratilgan User obyekti.
    """
    try:
        new_user = User(
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            language_code=language_code,
            balance=0.0,  # Boshlang'ich balans 0
            is_admin=False, # Dastlab admin emas
            user_status=user_status
        )
        session.add(new_user)
        # session.commit() va session.refresh() DbSessionMiddleware tomonidan bajariladi
        logger.info(f"Yangi foydalanuvchi qo'shildi: {telegram_id}")
        return new_user
    except Exception as e:
        logger.error(f"Yangi foydalanuvchini qo'shishda xatolik: {e}", exc_info=True)
        raise # Xatolikni yuqoriga uzatamiz

async def update_user(
    session: AsyncSession,
    telegram_id: int,
    **kwargs: Any
) -> Optional[User]:
    """
    Foydalanuvchi ma'lumotlarini yangilaydi.

    Args:
        session (AsyncSession): Ma'lumotlar bazasi sessiyasi.
        telegram_id (int): Foydalanuvchining Telegram ID'si.
        **kwargs: Yangilanadigan ustunlar va ularning qiymatlari.

    Returns:
        Optional[User]: Yangilangan User obyekti, agar topilsa, aks holda None.
    """
    try:
        user = await get_user_by_telegram_id(session, telegram_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            # session.commit() va session.refresh() DbSessionMiddleware tomonidan bajariladi
            logger.info(f"Foydalanuvchi {telegram_id} ma'lumotlari yangilandi.")
            return user
        logger.warning(f"Foydalanuvchi {telegram_id} topilmadi, yangilash mumkin emas.")
        return None
    except Exception as e:
        logger.error(f"Foydalanuvchi ma'lumotlarini yangilashda xatolik: {e}", exc_info=True)
        raise # Xatolikni yuqoriga uzatamiz