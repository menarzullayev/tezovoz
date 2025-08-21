# app/handlers/admin/settings_handler.py
# FIX-107
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject, and_f
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger
from aiogram.utils.i18n import I18n

from app.db.models.settings import Settings as SettingsModel
from app.middlewares.permission import PermissionMiddleware
from app.core.constants.i18n_texts import I18nKeys

router = Router()
# Bu routerdagi barcha handlerlar faqat adminlar uchun ishlashini ta'minlaymiz
router.message.middleware(PermissionMiddleware())
router.message.filter(F.is_admin == True)
router.callback_query.middleware(PermissionMiddleware())
router.callback_query.filter(F.is_admin == True)


@router.message(Command("set_voting_mode"))
async def set_voting_mode(message: Message, command: CommandObject, session: AsyncSession, i18n: I18n):
    """Ovoz berish rejimini o'zgartirish uchun handler."""
    # FIX-107: `message.from_user` obyekti mavjudligini tekshirish
    if not message.from_user:
        return
        
    logger.info(f"Debug: Admin {message.from_user.id} set_voting_mode buyrug'ini ishga tushirdi. Args: {command.args}")
    
    if not command.args:
        text = i18n.gettext("set-voting-mode-no-args-error", locale=message.from_user.language_code)
        await message.answer(text)
        logger.warning("Debug: set_voting_mode uchun argumentlar topilmadi.")
        return
    
    mode = command.args.strip()
    if mode not in ["auto", "manual"]:
        text = i18n.gettext("set-voting-mode-invalid-error", locale=message.from_user.language_code)
        await message.answer(text)
        logger.warning(f"Debug: Noto'g'ri rejim kiritildi: {mode}")
        return

    setting = await session.scalar(select(SettingsModel).where(SettingsModel.key == "VOTING_MODE"))
    if setting:
        logger.debug(f"Debug: VOTING_MODE sozlamasi yangilanmoqda. {setting.value} -> {mode}")
        setting.value = mode
    else:
        logger.debug(f"Debug: VOTING_MODE sozlamasi yaratilmoqda: {mode}")
        session.add(SettingsModel(key="VOTING_MODE", value=mode))

    await session.commit()
    text = i18n.gettext("set-voting-mode-success", locale=message.from_user.language_code).format(mode=mode)
    await message.answer(text)
    logger.info(f"Debug: Ovoz berish rejimi '{mode}' ga o'zgartirildi.")


@router.message(Command("set_voting_link"))
async def set_voting_link(message: Message, command: CommandObject, session: AsyncSession, i18n: I18n):
    """Qo'lda ovoz berish uchun havolani o'rnatish."""
    # FIX-107: `message.from_user` obyekti mavjudligini tekshirish
    if not message.from_user:
        return
        
    logger.info(f"Debug: Admin {message.from_user.id} set_voting_link buyrug'ini ishga tushirdi. Args: {command.args}")

    if not command.args or not command.args.startswith("http"):
        text = i18n.gettext("set-voting-link-invalid-error", locale=message.from_user.language_code)
        await message.answer(text)
        logger.warning(f"Debug: Noto'g'ri havola kiritildi: {command.args}")
        return

    link = command.args.strip()
    setting = await session.scalar(select(SettingsModel).where(SettingsModel.key == "MANUAL_VOTING_LINK"))
    if setting:
        logger.debug(f"Debug: MANUAL_VOTING_LINK sozlamasi yangilanmoqda. {setting.value} -> {link}")
        setting.value = link
    else:
        logger.debug(f"Debug: MANUAL_VOTING_LINK sozlamasi yaratilmoqda: {link}")
        session.add(SettingsModel(key="MANUAL_VOTING_LINK", value=link))

    await session.commit()
    text = i18n.gettext("set-voting-link-success", locale=message.from_user.language_code)
    await message.answer(text)
    logger.info(f"Debug: Qo'lda ovoz berish uchun havola o'rnatildi.")


@router.message(Command("get_settings"))
async def get_current_settings(message: Message, session: AsyncSession, i18n: I18n):
    """Joriy sozlamalarni ko'rish."""
    # FIX-107: `message.from_user` obyekti mavjudligini tekshirish
    if not message.from_user:
        return
        
    logger.info(f"Debug: Admin {message.from_user.id} get_settings buyrug'ini ishga tushirdi.")
    
    try:
        mode_setting = await session.scalar(select(SettingsModel).where(SettingsModel.key == "VOTING_MODE"))
        link_setting = await session.scalar(select(SettingsModel).where(SettingsModel.key == "MANUAL_VOTING_LINK"))
    except Exception as e:
        logger.error(f"Debug: Sozlamalarni DB'dan o'qishda xatolik: {e}", exc_info=True)
        await message.answer(i18n.gettext(I18nKeys.ERROR_OCCURRED, locale=message.from_user.language_code))
        return

    mode = mode_setting.value if mode_setting else i18n.gettext("auto-default", locale=message.from_user.language_code)
    link = link_setting.value if link_setting else i18n.gettext("not-set", locale=message.from_user.language_code)
    
    text = i18n.gettext("current-settings-info", locale=message.from_user.language_code).format(
        mode=mode,
        link=link
    )
    await message.answer(text)
    logger.debug("Debug: Joriy sozlamalar yuborildi.")
