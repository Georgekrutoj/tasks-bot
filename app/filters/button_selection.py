from aiogram.types import CallbackQuery
from aiogram.filters import BaseFilter


class ButtonSelectionFilter(BaseFilter):
    def __init__(
            self,
            valid_actions: list[str]
    ) -> None:
        self.valid_actions = valid_actions

    async def __call__(
            self,
            callback_query: CallbackQuery
    ) -> bool:
        callback_data = callback_query.data.split(" ")

        if len(callback_data) != 2:
            return False

        action = callback_data[1]
        return action in self.valid_actions
