from aiogram import Router
from aiogram import types
from aiogram.filters.command import Command

from app.objects import Tasks
from app.objects import UnknownTeacherError

router = Router()


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
