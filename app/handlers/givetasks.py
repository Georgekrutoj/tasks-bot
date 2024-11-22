from aiogram import Router
from aiogram import F
from aiogram import types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from app.states import SaveTaskConfig

router = Router()
tasks = {}


@router.message(Command("givetasks"))
async def give_tasks_command(message: types.Message) -> None:
    await message.answer(...)
