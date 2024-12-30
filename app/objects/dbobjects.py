from typing import Optional
from typing import Literal
from typing import override


class BaseData:
    def __init__(
            self,
            telegram_id: int
    ) -> None:
        self.telegram_id = telegram_id

    def __call__(self) -> tuple[int]:
        return self.telegram_id,


class Teacher(BaseData):
    def __init__(
            self,
            *,
            telegram_id: int,
            full_name: str
    ) -> None:
        super().__init__(telegram_id)

        self.full_name = full_name

    @override
    def __call__(self) -> tuple[int, str]:
        return self.telegram_id, self.full_name


class Student(BaseData):
    def __init__(
            self,
            *,
            telegram_id: int,
            name: str,
            teacher: int,
            tasks: Optional[list] = None,
            statistics: Optional[dict] = None
    ) -> None:
        super().__init__(telegram_id)

        self.name = name
        self.teacher = teacher
        self.tasks = tasks
        self.statistics = statistics

    @override
    def __call__(self) -> tuple[int, str, int, list | None, list | None]:
        return self.telegram_id, self.name, self.teacher, self.tasks, self.statistics


class Task(BaseData):
    def __init__(
            self,
            *,
            telegram_id: int,
            title: str,
            description: str,
            right_answer: str,
            level: Literal["Сложно", "Средне", "Легко"]
    ) -> None:
        super().__init__(telegram_id)

        self.title = title
        self.description = description
        self.right_answer = right_answer
        self.level = level

    @override
    def __call__(self) -> tuple[int, str, str, str, str]:
        return self.telegram_id, self.title, self.description, self.right_answer, self.level
