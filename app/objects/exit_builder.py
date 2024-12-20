from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


class ExitBuilder(InlineKeyboardBuilder):
    def __init__(
            self,
            buttons: list[types.InlineKeyboardButton] = None,
            adjust: int = 1,
    ) -> None:
        super().__init__()

        buttons = buttons or []
        close_button = types.InlineKeyboardButton(
            text="Отмена",
            callback_data="close"
        )

        self.add(*buttons, close_button)
        self.adjust(adjust)
