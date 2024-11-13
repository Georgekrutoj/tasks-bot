from aiogram import Router
from aiogram import F
from aiogram import types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from app.states import SaveAnswer

router = Router()


@router.message(Command("register"))
async def register_command(message: types.Message) -> None:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Я учитель",
        callback_data="teacher"
    ))
    builder.add(types.InlineKeyboardButton(
        text="Я ученик",
        callback_data="student"
    ))

    await message.answer("Вы учитель или ученик?", reply_markup=builder.as_markup())


@router.callback_query(F.data == "teacher")
async def register_as_teacher(callback: types.CallbackQuery) -> None:
    message = callback.message

    await message.delete()
    await message.answer(
        text=f"Ваш ID - <code>{message.from_user.id}</code>.\nДайте его ученикам, чтобы они зарегистрировались на Вас.",
        parse_mode=ParseMode.HTML
    )


@router.callback_query(F.data == "student")
async def register_as_student(callback: types.CallbackQuery, state: FSMContext) -> None:
    message = callback.message

    await message.delete()
    await message.answer("Пожалуйста, отправьте ID своего учителя")
    await state.set_state(SaveAnswer.waiting_for_teacher_id)


@router.message(SaveAnswer.waiting_for_teacher_id, F.text)
async def get_teacher_id(message: types.Message, state: FSMContext) -> None:
    teacher_id = message.text

    await state.update_data(teacher_id=teacher_id)
    await state.clear()
    await message.answer(f"ID учителя сохранен: {teacher_id}")
