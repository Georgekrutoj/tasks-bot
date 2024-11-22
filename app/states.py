from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup


class SaveTeacherID(StatesGroup):
    waiting_for_teacher_id = State()


class SaveTaskConfig(StatesGroup):
    waiting_for_title = State()
    waiting_for_text = State()  # Text of the task. Example: What is 1 + 1?
    waiting_for_right_answer = State()
    waiting_for_level = State()  # So like: Hard, Middle, Low
    waiting_for_recipients = State()
