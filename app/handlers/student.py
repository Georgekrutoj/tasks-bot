from aiogram import Router
from aiogram import F
from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from ..states import TasksSolving
from ..objects import Tasks
from ..utils import exit_state

router = Router()


@router.message(Command("solvetask"))
async def send_tasks(
        message: types.Message,
        state: FSMContext
) -> None:
    database = Tasks()
    user_id = message.from_user.id

    if database.does_teacher_exist(user_id):
        await message.answer("Только ученики могут решать задачи!")
        return

    tasks = database.get_student_tasks_names(user_id)
    builder = ReplyKeyboardBuilder([[
        types.KeyboardButton(text=title) for title in tasks
    ]])
    builder.add(types.KeyboardButton(text="Отмена"))
    builder.adjust(1)

    await message.answer(
        text="Выберите, какое задание Вы хотите решить.",
        reply_markup=builder.as_markup()
    )
    await state.set_state(TasksSolving.waiting_for_title)


@router.message(TasksSolving.waiting_for_title, F.text)
async def send_solution(
        message: types.Message,
        state: FSMContext
) -> None:
    if message.text == "Отмена":
        await exit_state(
            message=message,
            state=state,
            delete_message=False
        )
        return

    task_title = message.text
    database = Tasks()
    teacher_id = database.get_teacher_of_student(message.from_user.id)

    await message.answer(
        text=f"Выбрано задание <b>{task_title}</b>\n"
             f"{database.get_task(teacher_id, task_title).description}\n"
             f"<i>Отправьте решение!</i>",
        parse_mode=ParseMode.HTML
    )
    await state.set_state(TasksSolving.waiting_for_solution)


@router.message(TasksSolving.waiting_for_solution, F.text)
async def solve_task(
        message: types.Message,
        state: FSMContext
) -> None:
    database = Tasks()
    solution = message.text
    user_teacher_id = database.get_teacher_of_student(message.from_user.id)

    await message.answer(solution)

    await state.clear()
