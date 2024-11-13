import asyncio

from aiogram import Bot
from aiogram import Dispatcher
from aiogram import types
from aiogram import F
from aiogram.enums import ParseMode
from aiogram.filters.command import Command

from .handlers import register

from .constants import TOKEN
from .constants import BOT_COMMANDS
from .constants import BOT_COMMANDS_FOR_MENU
from .constants import ABOUT_BOT

bot = Bot(TOKEN)
dispatcher = Dispatcher()
dispatcher.include_router(register.router)


async def setup_bot() -> None:
    await bot.set_my_commands(BOT_COMMANDS_FOR_MENU)


@dispatcher.message(Command("start"))
async def start_command(message: types.Message) -> None:
    await message.answer(f"Доброго времени суток, {message.from_user.first_name}!")


@dispatcher.message(Command("about"))
async def about_command(message: types.Message) -> None:
    await message.answer(ABOUT_BOT)


@dispatcher.message(Command("help"))
async def help_command(message: types.Message) -> None:
    await message.answer("\n".join(["".join(tpl) for tpl in BOT_COMMANDS]))


@dispatcher.message(F.text)
async def another_command(message: types.Message) -> None:
    await message.answer("Команда не найдена. Чтобы просмотреть список команд, отправьте /help")


async def main() -> None:
    dispatcher.startup.register(setup_bot)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
