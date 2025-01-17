from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup


class SaveTeacherID(StatesGroup):
    waiting_for_teacher_id = State()


class TaskCreation(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()  # Text of the task. Example: What is 1 + 1?
    waiting_for_right_answer = State()
    waiting_for_level = State()  # So like: Hard, Middle, Low


class TasksGiving(StatesGroup):
    waiting_for_title = State()
    waiting_for_students = State()


class TasksGetting(StatesGroup):
    waiting_for_title = State()
