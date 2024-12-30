import asyncio

from aiogram import Bot
from aiogram import Dispatcher
from aiogram import types
from aiogram import F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from aiogram.filters.command import Command
from aiogram.filters.command import CommandStart

from .handlers import register
from .handlers import teacher

from .constants import TOKEN
from .constants import BOT_COMMANDS
from .constants import BOT_COMMANDS_FOR_MENU
from .constants import ABOUT_BOT

bot = Bot(TOKEN)
dispatcher = Dispatcher()
dispatcher.include_routers(register.router, teacher.router)


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


@dispatcher.callback_query(F.data == "close")
async def close_command(
        callback: types.CallbackQuery,
        state: FSMContext
) -> None:
    message = callback.message

    await state.clear()
    await message.delete()
    await message.answer("Действие отменено")


async def main() -> None:
    dispatcher.startup.register(setup_bot)

    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    print("Bot has been successfully started!")
    asyncio.run(main())
