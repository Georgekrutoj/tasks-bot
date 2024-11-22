from aiogram.types import BotCommand

TOKEN = "7664798196:AAGaUrMwFG8vWAvGrOwl9wOJloWzeLLCb2w"
BOT_COMMANDS = [
    ("/start", " - запустить бота"),
    ("/about", " - информация о боте"),
    ("/help", " - получить список команд"),
    ("/register", " - зарегистрироваться"),
    ("/deleteuser", " - удалить аккаунт"),
    ("/students", " - получить своих студентов"),
    ("/givetasks", " - дать задания")
]
BOT_COMMANDS_FOR_MENU = [BotCommand(command=cmd, description=description) for cmd, description in BOT_COMMANDS]
ABOUT_BOT = """Этот бот используется для \
обмена задачами между учениками и учителем"""
PATH_TO_DB = "databases\\tasks.db"
