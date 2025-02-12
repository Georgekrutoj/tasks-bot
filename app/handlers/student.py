from aiogram import Router
from aiogram import F
from aiogram import types
from aiogram.filters.command import Command

from ..objects import Tasks

router = Router()


@router.message(Command("getmytasks"))
async def get_student_tasks(message: types.Message) -> None:
    database = Tasks()
    tasks = database.get_student_tasks(message.from_user.id)

    await message.answer(tasks)
