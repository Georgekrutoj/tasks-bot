from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup


class SaveAnswer(StatesGroup):
    waiting_for_teacher_id = State()
