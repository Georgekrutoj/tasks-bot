from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove

from aiogram.fsm.context import FSMContext

from typing import Optional


async def exit_state(
        *,
        message: Message,
        state: FSMContext,
        delete_text: Optional[str] = "Действие успешно отменено.",
        delete_message: bool = True
) -> None:
    if delete_message:
        await message.delete()

    await state.clear()
    await message.answer(
        text=delete_text,
        reply_markup=ReplyKeyboardRemove()
    )
