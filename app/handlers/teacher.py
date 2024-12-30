from aiogram import Router
from aiogram import F
from aiogram import types
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

from app.states import TaskCreation

from app.constants import TASK_CREATION_TEXT
from app.constants import ERROR_MESSAGE

from app.objects import ExitBuilder
from app.objects import Tasks
from app.objects import Task
from app.objects import UnknownTeacherError

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
async def get_task_name(
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
        await state.update_data(task_name=message.text)
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
    levels = {
        "hard": "Сложно",
        "middle": "Средне",
        "easy": "Легко"
    }
    await state.update_data(level=levels[callback.data])
    data = await state.get_data()
    message = callback.message

    await message.delete()
    await message.answer(
        text=f"Название: {data.get("task_name")}\n"
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
        title=data.get("task_name"),
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
