import asyncio
import json

from aiogram import Bot
from aiogram import Dispatcher
from aiogram import types
from aiogram import F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from aiogram.filters.command import Command
from aiogram.filters.command import CommandStart

from .handlers import register
from .handlers import teacher
from .handlers import student

from .utils import exit_state

from .constants import TOKEN
from .constants import BOT_COMMANDS
from .constants import BOT_COMMANDS_FOR_MENU
from .constants import ABOUT_BOT
from .constants import ERROR_MESSAGE

from .objects import Tasks
from .objects import Task

from .states import TasksGetting

bot = Bot(TOKEN)
dispatcher = Dispatcher()
dispatcher.include_routers(register.router, teacher.router, student.router)


async def setup_bot() -> None:
    await bot.set_my_commands(BOT_COMMANDS_FOR_MENU)


@dispatcher.message(CommandStart())
async def start_command(message: types.Message) -> None:
    await message.answer(f"Приветствую, {message.from_user.first_name}!\nЧтобы просмотреть список команд - /help")


@dispatcher.message(Command("about"))
async def about_command(message: types.Message) -> None:
    await message.answer(ABOUT_BOT)


@dispatcher.message(Command("help"))
async def help_command(message: types.Message) -> None:
    await message.answer("\n".join(["".join(cmd) for cmd in BOT_COMMANDS]))


@dispatcher.message(Command("getid"))
async def get_id(message: types.Message) -> None:
    await message.answer(
        text=f"Ваш <i>ID</i> — <code>{message.from_user.id}</code>.",
        parse_mode=ParseMode.HTML
    )


@dispatcher.message(Command("gettasks"))
async def get_tasks(
        message: types.Message,
        state: FSMContext
) -> None:
    database = Tasks()
    user_id = message.from_user.id
    tasks = database.get_tasks(user_id) if database.does_teacher_exist(user_id) else \
        database.get_student_tasks_names(user_id)

    if len(tasks) == 0:
        await message.answer("Вы не можете просмотреть задачи, так как их нет.")
    else:
        print(tasks)

        if isinstance(tasks[0], Task):
            builder = ReplyKeyboardBuilder([[types.KeyboardButton(
                text=task.title
            )] for task in tasks]
            )
        else:
            builder = ReplyKeyboardBuilder([[types.KeyboardButton(
                text=title
            )] for title in tasks])

        builder.add(types.KeyboardButton(text="Отмена"))
        builder.adjust(1)

        await message.answer(
            text="Выберите задачу, которую Вы хотите просмотреть.",
            reply_markup=builder.as_markup()
        )
        await state.update_data(teacher_id=database.get_teacher_of_student(message.from_user.id))
        await state.set_state(TasksGetting.waiting_for_title)


@dispatcher.message(TasksGetting.waiting_for_title, F.text)
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

    data = await state.get_data()
    teacher_id = data.get("teacher_id")
    database = Tasks()

    try:
        task = database.get_task(message.from_user.id if teacher_id is None else teacher_id, message.text)
        await message.answer(str(task) if task else "Такого задания нет.")
    except Exception as e:
        print(e)
        await message.answer(ERROR_MESSAGE)


@dispatcher.callback_query(F.data == "close")
async def close_command(
        callback: types.CallbackQuery,
        state: FSMContext
) -> None:
    await exit_state(
        message=callback.message,
        state=state
    )


async def main() -> None:
    dispatcher.startup.register(setup_bot)

    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    print("Bot has been successfully started!")
    asyncio.run(main())
