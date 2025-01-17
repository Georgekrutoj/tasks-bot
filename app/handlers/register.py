from aiogram import Router
from aiogram import F
from aiogram import types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from app.states import SaveTeacherID
from app.constants import ERROR_MESSAGE

from app.objects import ExitBuilder
from app.objects import Teacher
from app.objects import Student
from app.objects import Tasks
from app.objects import UserAlreadyExistsError
from app.objects import UserDoesNotExistError
from app.objects import UnknownTeacherError

router = Router()


@router.message(Command("register"))
async def register_command(
        message: types.Message,
        state: FSMContext
) -> None:
    builder = ExitBuilder(
        [
            types.InlineKeyboardButton(
                text="Я учитель",
                callback_data="teacher"
            ),
            types.InlineKeyboardButton(
                text="Я ученик",
                callback_data="student"
            )
        ]
    )

    await state.update_data(telegram_id=message.from_user.id, full_name=message.from_user.full_name)
    await message.answer("Вы учитель или ученик?", reply_markup=builder.as_markup())


@router.message(Command("deleteuser"))
async def delete_user(
        message: types.Message,
        state: FSMContext
) -> None:
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
            callback_data="close"
        )
    )
    builder.adjust(1)

    await state.update_data(telegram_id=message.from_user.id)
    await message.answer(
        text="<b>Вы точно хотите удалить аккаунт?</b>\n",
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )


@router.callback_query(F.data == "teacher")
async def register_as_teacher(
        callback: types.CallbackQuery,
        state: FSMContext
) -> None:
    data = await state.get_data()
    user_id = data.get("telegram_id")
    message = callback.message
    database = Tasks()
    teacher = Teacher(
        telegram_id=user_id,
        full_name=data.get("full_name")
    )

    try:
        database.add(teacher)
        await message.delete()
        await message.answer(
            text=f"Ваш ID - <code>{user_id}</code> (<i>нажмите, чтобы скопировать</i>).\n"
                 f"Дайте его ученикам, чтобы они зарегистрировались на Вас.\n"
                 f"Захотите удалить аккаунт - /deleteuser",
            parse_mode=ParseMode.HTML
        )
        await callback.answer("Вы успешно зарегистрировались как учитель!")
    except UserAlreadyExistsError:
        await message.answer("Кажется, Вы уже зарегистрированы.\nЕсли хотите удалить аккаунт, отправьте /deleteuser")
    except Exception as e:
        print(e)
        await message.answer(ERROR_MESSAGE)
    finally:
        database.close()
        await state.clear()


@router.callback_query(F.data == "student")
async def register_as_student(
        callback: types.CallbackQuery,
        state: FSMContext
) -> None:
    message = callback.message
    builder = ExitBuilder()

    await message.delete()
    await message.answer("Пожалуйста, отправьте ID своего учителя", reply_markup=builder.as_markup())
    await state.set_state(SaveTeacherID.waiting_for_teacher_id)


@router.callback_query(F.data == "delete_sure")
async def delete_user(
        callback: types.CallbackQuery,
        state: FSMContext
) -> None:
    data = await state.get_data()
    id_ = data.get("telegram_id")
    message = callback.message
    database = Tasks()

    try:
        database.del_user(id_)
        await message.answer("Ваш профиль успешно удалён.")
    except UserDoesNotExistError:
        await message.answer("Вы не можете удалить свой профиль, так как Вы не зарегистрированы.")
    except Exception as e:
        print(e)
        await message.answer(ERROR_MESSAGE)
    finally:
        database.close()
        await state.clear()


@router.message(SaveTeacherID.waiting_for_teacher_id, F.text)
async def get_teacher_id(
        message: types.Message,
        state: FSMContext
) -> None:
    data = await state.get_data()
    teacher_id = message.text
    database = Tasks()

    try:
        student = Student(
            telegram_id=data.get("telegram_id"),
            name=data.get("full_name"),
            teacher=int(teacher_id)
        )

        database.add(student)

        await message.delete()
        await message.answer(f"Вы успешно зарегистрировались как ученик!")
    except UserAlreadyExistsError:
        await message.answer("Кажется, Вы уже зарегистрированы.\nЕсли хотите удалить аккаунт, отправьте /deleteuser")
    except UnknownTeacherError:
        await message.answer("Кажется, нет учителя с таким ID...")
    except Exception as e:
        print(e)
        await message.answer(ERROR_MESSAGE)
    finally:
        database.close()
        await state.clear()
