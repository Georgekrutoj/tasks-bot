from aiogram import Router
from aiogram import F
from aiogram import types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from app.states import SaveTeacherID

from app.objects import CloseButton
from app.objects import Level

router = Router()
close_button = CloseButton()


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
    builder.add(close_button)
    builder.adjust(1)

    await message.answer("Вы учитель или ученик?", reply_markup=builder.as_markup())


@router.message(Command("deleteuser"))
async def delete_user(message: types.Message) -> None:
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Да",
            callback_data="delete_sure"
        )
    )
    builder.add(
        types.InlineKeyboardButton(
            text="Нет",
            callback_data="delete_not_sure"
        )
    )
    builder.adjust(1)

    await message.answer(
        text="<b>Вы точно хотите удалить аккаунт?</b>\n",
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )


@router.callback_query(F.data == "teacher")
async def register_as_teacher(callback: types.CallbackQuery) -> None:
    message = callback.message

    await message.delete()
    await message.answer(
        text=f"Ваш ID - <code>{message.from_user.id}</code> (<i>нажмите, чтобы скопировать</i>).\n"
             f"Дайте его ученикам, чтобы они зарегистрировались на Вас.\n"
             f"Захотите удалить аккаунт - /deleteuser",
        parse_mode=ParseMode.HTML
    )
    await callback.answer("Вы успешно зарегистрировались как учитель!")


@router.callback_query(F.data == "student")
async def register_as_student(callback: types.CallbackQuery, state: FSMContext) -> None:
    message = callback.message
    builder = InlineKeyboardBuilder()
    builder.add(close_button)

    await message.delete()
    await message.answer("Пожалуйста, отправьте ID своего учителя", reply_markup=builder.as_markup())
    await state.set_state(SaveTeacherID.waiting_for_teacher_id)


@router.message(SaveTeacherID.waiting_for_teacher_id, F.text)
async def get_teacher_id(message: types.Message, state: FSMContext) -> None:
    teacher_id = message.text

    await state.update_data(teacher_id=teacher_id)
    await state.clear()
    await message.answer(f"ID учителя сохранен: {teacher_id}")
