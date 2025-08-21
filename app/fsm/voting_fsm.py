# FIX-190
# app/fsm/voting_fsm.py

from aiogram.fsm.state import State, StatesGroup

class VotingStates(StatesGroup):
    """
    Ovoz berish jarayonining FSM holatlari.
    """
    waiting_for_phone_number = State()
    waiting_for_project_id = State()
    waiting_for_captcha = State()
    waiting_for_otp = State()
    waiting_for_confirmation = State() # YANGI HOLAT
    waiting_for_screenshot = State()
