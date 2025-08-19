# NEW-138
# app/fsm/voting_fsm.py

from aiogram.fsm.state import State, StatesGroup

class VotingStates(StatesGroup):
    """
    Ovoz berish jarayonining FSM holatlari.
    """
    waiting_for_phone_number = State()  # Foydalanuvchidan telefon raqami kutilmoqda
    waiting_for_captcha = State()       # Foydalanuvchidan captcha javobi kutilmoqda
    waiting_for_otp = State()           # Foydalanuvchidan OTP kodi kutilmoqda
