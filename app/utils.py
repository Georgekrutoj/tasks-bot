from aiogram import types
from aiogram.fsm.context import FSMContext

from .objects import Tasks
from .objects.student_for_tasks_giving import StudentForTasksGiving

from typing import Optional


async def exit_state(
        *,
        message: types.Message,
        state: FSMContext,
        exit_text: Optional[str] = "Действие успешно отменено.",
        delete_message: bool = True,
        database: Optional[Tasks] = None
) -> None:
    if delete_message:
        await message.delete()

    if exit_text:
        await message.answer(
            text=exit_text,
            reply_markup=types.ReplyKeyboardRemove()
        )

    if database is not None:
        database.close()

    await state.clear()


def get_buttons_texts(inline_keyboard: list[list[types.InlineKeyboardButton]]) -> list[str | StudentForTasksGiving]:
    texts = []

    for row in inline_keyboard:
        for button in row:
            callback_data = button.callback_data

            if "selected_student" in callback_data:
                texts.append(StudentForTasksGiving(button.text, int(button.callback_data.split()[0])))
            elif "selected_task" in callback_data:
                texts.append(button.text)

    return texts


def is_any_selected(inline_keyboard: list[list[types.InlineKeyboardButton]]) -> bool:
    buttons_texts = get_buttons_texts(inline_keyboard)

    if "✅" in "".join(map(str, buttons_texts)):
        return True
    return False


def get_selected(inline_keyboard: list[list[types.InlineKeyboardButton]]) -> list[str]:
    buttons_texts = get_buttons_texts(inline_keyboard)
    selected = []

    for button_text in buttons_texts:
        string_button_text = str(button_text)

        if "✅" in string_button_text:
            selected.append(string_button_text[1:])

    return selected
