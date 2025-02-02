from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .dbobjects import Task
from .dbobjects import Student

from .enums import ExitButtonPosition


class ExitBuilder(InlineKeyboardBuilder):
    def __init__(
            self,
            buttons: list[types.InlineKeyboardButton] = None,
            exit_button_position: ExitButtonPosition = ExitButtonPosition.DOWN,
            adjust: int = 1
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
        ...  # TODO: Create this func


class TasksBuilder(ExitBuilder):
    def __init__(
            self,
            tasks: list[Task]
    ) -> None:
        buttons = []

        for index, task in enumerate(tasks):
            buttons.append(
                types.InlineKeyboardButton(
                    text=task.title,
                    callback_data=f"{index} selected_task"
                )
            )

        super().__init__(buttons)


class StudentsBuilder(ExitBuilder):
    def __init__(
            self,
            students: list[Student]
    ) -> None:
        buttons = []

        for student in students:
            buttons.append(
                types.InlineKeyboardButton(
                    text=student.name,
                    callback_data=f"{student.telegram_id} selected_student"
                )
            )

        super().__init__(buttons)
