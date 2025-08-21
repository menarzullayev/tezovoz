# FIX-206
# app/handlers/admin/user_management.py

from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.db.models.users import User
from app.db.models.enums import UserStatusEnum
from app.db.queries.user_crud_queries import update_user, get_user_by_telegram_id
from app.utils.admin_utils import send_user_status_notification
from app.core.constants.i18n_texts import I18nKeys
from aiogram.utils.i18n import I18n

router = Router()

@router.message(Command(commands=["block_user"]))
async def block_user_handler(message: Message, command: CommandObject, session: AsyncSession, bot: Bot, i18n: I18n):
    """
    Admin buyrug'i orqali foydalanuvchini bloklaydi.
    Masalan: /block_user <user_id>
    """
    if not command.args or not command.args.isdigit():
        await message.answer("❌ Foydalanuvchi ID'sini to'g'ri kiriting. Namuna: `/block_user 123456789`", parse_mode="Markdown")
        return

    target_user_id = int(command.args)
    user_db = await get_user_by_telegram_id(session, target_user_id)
    
    if not user_db:
        await message.answer(f"❌ Foydalanuvchi `{target_user_id}` topilmadi.", parse_mode="Markdown")
        return
    
    if user_db.user_status == UserStatusEnum.BLOCKED:
        await message.answer(f"⚠️ Foydalanuvchi `{target_user_id}` allaqachon bloklangan.")
        return

    await update_user(session, target_user_id, user_status=UserStatusEnum.BLOCKED)
    await session.commit()
    
    notification_text = i18n.gettext(I18nKeys.USER_BLOCKED_NOTIFICATION, locale=user_db.language_code)
    await send_user_status_notification(bot, target_user_id, notification_text)
    
    await message.answer(f"✅ Foydalanuvchi `{target_user_id}` muvaffaqiyatli bloklandi.", parse_mode="Markdown")


@router.message(Command(commands=["unblock_user"]))
async def unblock_user_handler(message: Message, command: CommandObject, session: AsyncSession, bot: Bot, i18n: I18n):
    """
    Admin buyrug'i orqali foydalanuvchini blokdan chiqaradi.
    Masalan: /unblock_user <user_id>
    """
    if not command.args or not command.args.isdigit():
        await message.answer("❌ Foydalanuvchi ID'sini to'g'ri kiriting. Namuna: `/unblock_user 123456789`", parse_mode="Markdown")
        return

    target_user_id = int(command.args)
    user_db = await get_user_by_telegram_id(session, target_user_id)
    
    if not user_db:
        await message.answer(f"❌ Foydalanuvchi `{target_user_id}` topilmadi.", parse_mode="Markdown")
        return
    
    if user_db.user_status == UserStatusEnum.ACTIVE:
        await message.answer(f"⚠️ Foydalanuvchi `{target_user_id}` allaqachon bloklanmagan.")
        return

    await update_user(session, target_user_id, user_status=UserStatusEnum.ACTIVE)
    await session.commit()
    
    notification_text = i18n.gettext(I18nKeys.USER_UNBLOCKED_NOTIFICATION, locale=user_db.language_code)
    await send_user_status_notification(bot, target_user_id, notification_text)
    
    await message.answer(f"✅ Foydalanuvchi `{target_user_id}` muvaffaqiyatli blokdan chiqarildi.", parse_mode="Markdown")
    
@router.message(Command(commands=["set_balance"]))
async def set_balance_handler(message: Message, command: CommandObject, session: AsyncSession, bot: Bot):
    """
    Admin buyrug'i orqali foydalanuvchi balansini o'zgartiradi.
    Masalan: /set_balance <user_id> <amount>
    """
    if not command.args:
        await message.answer("❌ Foydalanuvchi ID'si va summani kiriting. Namuna: `/set_balance 123456789 5000`", parse_mode="Markdown")
        return
        
    args = command.args.split()
    if len(args) != 2 or not args[0].isdigit() or not args[1].replace('.', '', 1).isdigit():
        await message.answer("❌ Buyruq formati noto'g'ri. Namuna: `/set_balance 123456789 5000`", parse_mode="Markdown")
        return

    target_user_id = int(args[0])
    amount = float(args[1])
    
    user_db = await get_user_by_telegram_id(session, target_user_id)
    if not user_db:
        await message.answer(f"❌ Foydalanuvchi `{target_user_id}` topilmadi.", parse_mode="Markdown")
        return
        
    await update_user(session, target_user_id, balance=amount)
    await session.commit()
    
    await message.answer(f"✅ Foydalanuvchi `{target_user_id}` balansi `{amount:,.0f}` so'mga o'zgartirildi.", parse_mode="Markdown")