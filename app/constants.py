from os import getenv
from dotenv import load_dotenv
from aiogram.types import BotCommand

load_dotenv("app\\.env")

TOKEN = getenv("BOT_TOKEN")
BOT_COMMANDS = [
    ("/start", " - запустить бота"),
    ("/about", " - информация о боте"),
    ("/help", " - получить список команд"),
    ("/register", " - зарегистрироваться"),
    ("/deleteuser", " - удалить аккаунт"),
    ("/getstudents", " - получить своих студентов"),
    ("/addtask", " - добавить задание"),
    ("/givetasks", " - дать задания"),
    ("/gettasks", " - получить список заданий для просмотра"),
    ("/getid", " - получить свой ID (бесполезно, если Вы не учитель)")
]
BOT_COMMANDS_FOR_MENU = [BotCommand(command=cmd, description=description) for cmd, description in BOT_COMMANDS]
ABOUT_BOT = """Этот бот используется для \
обмена задачами между учениками и учителем"""
PATH_TO_DB = "app\\databases\\tasks.db"
ERROR_MESSAGE = "Что-то пошло не так! Повторите попытку позже."
TASK_CREATION_TEXT = "{} есть. Теперь, пожалуйста, отправьте <b>{}</b>."
