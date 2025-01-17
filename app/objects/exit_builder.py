from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .exit_button_position import ExitButtonPosition


class ExitBuilder(InlineKeyboardBuilder):
    def __init__(
            self,
            buttons: list[types.InlineKeyboardButton] = None,
            adjust: int = 1,
            exit_button_position: ExitButtonPosition = ExitButtonPosition.DOWN
    ) -> None:
        super().__init__()

        close_button = types.InlineKeyboardButton(
            text="Отмена",
            callback_data="close"
        )

        if buttons is None:
            buttons = []

        if exit_button_position == ExitButtonPosition.UP:
            self.add(close_button, *buttons)
        elif exit_button_position == ExitButtonPosition.DOWN:
            self.add(*buttons, close_button)

        self.adjust(adjust)

    def arrange_buttons(self) -> None:
        ...
