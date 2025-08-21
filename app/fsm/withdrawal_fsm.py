# app/fsm/withdrawal_fsm.py
from aiogram.fsm.state import State, StatesGroup

class WithdrawalStates(StatesGroup):
    waiting_for_card_number = State()
    waiting_for_amount = State()
