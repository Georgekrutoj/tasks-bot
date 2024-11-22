from aiogram.types import InlineKeyboardButton


class CloseButton(InlineKeyboardButton):
    def __init__(self) -> None:
        super().__init__(text="Отмена", callback_data="close")
