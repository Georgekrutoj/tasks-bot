from aiogram import Router
from aiogram import F
from aiogram import types
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from app.utils import exit_state

from app.states import TaskCreation
from app.states import TasksGetting

from app.constants import TASK_CREATION_TEXT
from app.constants import ERROR_MESSAGE

from app.objects import ExitBuilder
from app.objects import Tasks
from app.objects import Task
from app.objects import UnknownTeacherError

from app.filters import ButtonSelectionFilter

LEVELS = {
    "hard": "Сложно",
    "middle": "Средне",
    "easy": "Легко"
}
router = Router()


@router.message(Command("addtask"))
async def add_task(
        message: types.Message,
        state: FSMContext
) -> None:
    database = Tasks()

    if database.is_teacher_exist(message.from_user.id):
        await state.update_data(user_id=message.from_user.id)
        await message.answer(
            text="<b>Вы попали в мастер по созданию задач.</b>\nПожалуйста, отправьте название задачи.",
            parse_mode=ParseMode.HTML,
            reply_markup=ExitBuilder().as_markup()
        )
        await state.set_state(TaskCreation.waiting_for_title)
    else:
        await message.answer("Создавать задачи может только учитель.")


@router.message(TaskCreation.waiting_for_title, F.text)
async def get_title(
        message: types.Message,
        state: FSMContext
) -> None:
    database = Tasks()

    if database.is_task_exist(message.text):
        await message.answer("Задание с таким названием уже существует. Попробуйте создать с другим.")
    else:
        await message.answer(
            text=TASK_CREATION_TEXT.format("Название", "описание задания"),
            parse_mode=ParseMode.HTML,
            reply_markup=ExitBuilder().as_markup()
        )
        await state.update_data(title=message.text)
        await state.set_state(TaskCreation.waiting_for_description)


@router.message(TaskCreation.waiting_for_description, F.text)
async def get_task_description(
        message: types.Message,
        state: FSMContext
) -> None:
    await message.answer(
        text=TASK_CREATION_TEXT.format("Описание задания", "правильный ответ"),
        parse_mode=ParseMode.HTML,
        reply_markup=ExitBuilder().as_markup()
    )
    await state.update_data(description=message.text)
    await state.set_state(TaskCreation.waiting_for_right_answer)


@router.message(TaskCreation.waiting_for_right_answer, F.text)
async def get_task_right_answer(
        message: types.Message,
        state: FSMContext
) -> None:
    builder = ExitBuilder([
        types.InlineKeyboardButton(
            text="Сложно",
            callback_data="hard"
        ),
        types.InlineKeyboardButton(
            text="Средне",
            callback_data="middle"
        ),
        types.InlineKeyboardButton(
            text="Легко",
            callback_data="easy"
        )
    ])

    await message.answer(
        text=TASK_CREATION_TEXT.format("Правильный ответ", "сложность"),
        parse_mode=ParseMode.HTML,
        reply_markup=builder.as_markup()
    )
    await state.update_data(right_answer=message.text)


@router.callback_query(F.data.in_({"hard", "middle", "easy"}))
async def get_level(
        callback: types.CallbackQuery,
        state: FSMContext
) -> None:
    await state.update_data(level=LEVELS[callback.data])
    data = await state.get_data()
    message = callback.message

    await message.delete()
    await message.answer(
        text=f"Название: {data.get("title")}\n"
             f"Описание: {data.get("description")}\n"
             f"Правильный ответ: {data.get("right_answer")}\n"
             f"Сложность: {data.get("level")}",
        parse_mode=ParseMode.HTML,
        reply_markup=ExitBuilder(
            [
                types.InlineKeyboardButton(
                    text="Подтвердить",
                    callback_data="confirm_task"
                )
            ]
        ).as_markup()
    )


@router.callback_query(F.data == "confirm_task")
async def confirm_task(
        callback: types.CallbackQuery,
        state: FSMContext
) -> None:
    data = await state.get_data()
    message = callback.message
    database = Tasks()
    task = Task(
        telegram_id=data.get("user_id"),
        title=data.get("title"),
        description=data.get("description"),
        right_answer=data.get("right_answer"),
        level=data.get("level")
    )

    try:
        database.add(task)
        await message.answer("Задача успешно добавлена!")
    except Exception as e:
        print(e)
        await message.answer(ERROR_MESSAGE)
    finally:
        database.close()
        await state.clear()


@router.message(Command("givetasks"))
async def give_tasks(message: types.Message) -> None:
    database = Tasks()

    try:
        builder = ExitBuilder([
            types.InlineKeyboardButton(
                text=task.title,
                callback_data=f"{index} task_selected"
            ) for index, task in enumerate(database.get_tasks(message.from_user.id))
        ])

        await message.answer(
            text="Выберете задания, которые Вы хотите дать.",
            reply_markup=builder.as_markup()
        )
    except UnknownTeacherError:
        await message.answer("Только учитель может давать задания!")
    finally:
        database.close()


@router.callback_query(ButtonSelectionFilter(["task_selected", "task_unselected"]))
async def select_task(callback: types.CallbackQuery) -> None:
    message = callback.message
    index = callback.data.split()[0]
    new_buttons = []

    for row in message.reply_markup.inline_keyboard:
        new_row = []

        for button in row:
            if button.callback_data.startswith(index) and button.callback_data.endswith("task_selected"):
                new_row.append(types.InlineKeyboardButton(
                    text="✅" + button.text,
                    callback_data=f"{index} task_unselected"
                ))
            elif button.callback_data.startswith(index) and button.callback_data.endswith("task_unselected"):
                new_row.append(types.InlineKeyboardButton(
                    text=button.text[1:],
                    callback_data=f"{index} task_selected"
                ))
            else:
                new_row.append(button)

        new_buttons.append(new_row)

    await message.edit_reply_markup(reply_markup=types.InlineKeyboardMarkup(inline_keyboard=new_buttons))


@router.message(Command("gettasks"))
async def get_tasks(
        message: types.Message,
        state: FSMContext
) -> None:
    database = Tasks()
    tasks = database.get_tasks(message.from_user.id)

    if len(tasks) == 0:
        await message.answer("Вы не можете просмотреть задачи, так как их нет.")
    else:
        builder = ReplyKeyboardBuilder([[types.KeyboardButton(text=task.title)] for task in tasks])
        builder.add(types.KeyboardButton(text="Отмена"))
        builder.adjust(1)

        await message.answer(
            text="Выберите задачу, которую Вы хотите просмотреть.",
            reply_markup=builder.as_markup()
        )
        await state.set_state(TasksGetting.waiting_for_title)


@router.message(TasksGetting.waiting_for_title, F.text)
async def get_task(
        message: types.Message,
        state: FSMContext
) -> None:
    if message.text == "Отмена":
        await exit_state(
            message=message,
            state=state,
            delete_message=False
        )
        return None

    database = Tasks()

    try:
        task = database.get_task(message.from_user.id, message.text)

        await message.answer(str(task) if task else "Такого задания нет.")
    except Exception as e:
        print(e)
        await message.answer(ERROR_MESSAGE)


@router.message(Command("getstudents"))
async def get_students(message: types.Message) -> None:
    database = Tasks()

    try:
        students = database.get_students(message.from_user.id)
        message_ = ""

        for student in students:
            message_ += f"Имя: {student.name}"

        if message_ == "":
            await message.answer("У Вас нет учеников.")
        else:
            await message.answer(message_)
    except UnknownTeacherError:
        await message.answer("Просмотреть своих учеников может только учитель.")
    finally:
        database.close()
