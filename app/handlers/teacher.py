from aiogram import Router
from aiogram import F
from aiogram import types
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.utils import exit_state
from app.utils import is_any_selected
from app.utils import get_selected

from app.states import TaskCreation
from app.states import TasksGetting

from app.constants import TASK_CREATION_TEXT
from app.constants import ERROR_MESSAGE

from app.objects import ExitBuilder
from app.objects import TasksBuilder
from app.objects import StudentsBuilder
from app.objects import Tasks
from app.objects import Task
from app.objects import UnknownTeacherError
from app.objects.student_for_tasks_giving import StudentForTasksGiving

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
        await exit_state(
            message=message,
            state=state,
            delete_text="",
            database=database
        )


@router.message(Command("givetasks"))
async def give_tasks(
        message: types.Message,
        state: FSMContext
) -> None:
    database = Tasks()
    students = database.get_students(message.from_user.id)

    if len(students) == 0:
        await message.answer("Чтобы дать задания, надо иметь учеников!")
        await exit_state(
            message=message,
            state=state,
            delete_text="",
            delete_message=False,
            database=database
        )
        return

    try:
        builder = TasksBuilder(database.get_tasks(message.from_user.id))
        builder.add(
            types.InlineKeyboardButton(
                text="Продолжить",
                callback_data="continue_to_students"
            )
        )

        await state.update_data(teacher_id=message.from_user.id)
        await message.answer(
            text="Выберете задания, которые Вы хотите дать. Для просмотра описаний задач используйте /gettasks",
            reply_markup=builder.as_markup()
        )
    except UnknownTeacherError:
        await message.answer("Только учитель может давать задания!")
    finally:
        database.close()


@router.callback_query(F.data == "continue_to_students")
async def select_students(
        callback: types.CallbackQuery,
        state: FSMContext
) -> None:
    message = callback.message

    if not is_any_selected(message.reply_markup.inline_keyboard):
        await callback.answer("Хотя бы одно задание должно быть выбрано!")
        return

    data = await state.get_data()
    teacher_id = data.get("teacher_id")
    database = Tasks()
    builder = StudentsBuilder(database.get_students(teacher_id))
    builder.add(types.InlineKeyboardButton(
        text="Продолжить",
        callback_data="continue_to_final"
    ))
    selected_tasks = get_selected(message.reply_markup.inline_keyboard)

    await message.edit_text(
        text=f"Выбранные задания: <b>{", ".join(selected_tasks)}</b>.\n"
             f"Выберите, кому Вы хотите их дать.",
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )
    await state.update_data(selected_tasks=selected_tasks)


@router.callback_query(F.data == "continue_to_final")
async def check_tasks_to_give(
        callback: types.CallbackQuery,
        state: FSMContext
) -> None:
    message = callback.message

    if not is_any_selected(message.reply_markup.inline_keyboard):
        await callback.answer("Хотя бы один ученик должен быть выбран!")
        return

    data = await state.get_data()
    selected_tasks = data.get("selected_tasks")
    selected_students = get_selected(message.reply_markup.inline_keyboard)
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Да", callback_data="give_tasks"))
    builder.add(types.InlineKeyboardButton(text="Нет", callback_data="close"))
    builder.adjust(1)
    print(selected_students)

    await message.edit_text(
        text=f"Выбранные задания: <b>{", ".join(selected_tasks)}</b>.\n"
             f"Выбранные ученики: <b>{", ".join(selected_students)}</b>.\n"
             f"Раздать задания?",
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )
    await state.update_data(selected_students=selected_students)


@router.callback_query(F.data == "give_tasks")
async def finally_give_tasks(
        callback: types.CallbackQuery,
        state: FSMContext
) -> None:
    ...


@router.callback_query(ButtonSelectionFilter([
    "selected_task", "unselected_task",
    "selected_student", "unselected_student"
]))
async def select_button(callback: types.CallbackQuery) -> None:
    message = callback.message
    new_buttons = []
    index = callback.data.split()[0]

    for row in message.reply_markup.inline_keyboard:
        new_row = []

        for button in row:
            if not button.callback_data or " " not in button.callback_data:
                new_row.append(button)
                continue

            split_data = button.callback_data.split()
            ends_with = split_data[1] if len(split_data) > 1 else ""
            does_start_with_index = button.callback_data.split()[0] == index

            if does_start_with_index and (ends_with == "selected_task" or ends_with == "selected_student"):
                new_row.append(types.InlineKeyboardButton(
                    text="✅" + button.text,
                    callback_data=f"{index} un{ends_with}"
                ))
            elif does_start_with_index and (ends_with == "unselected_task" or ends_with == "unselected_student"):
                new_row.append(types.InlineKeyboardButton(
                    text=button.text[1:],
                    callback_data=f"{index} {ends_with[2:]}"
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
