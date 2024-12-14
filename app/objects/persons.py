from typing import Optional


class BasePerson:
    def __init__(
            self,
            telegram_id: int
    ) -> None:
        self.telegram_id = telegram_id

    def __call__(self) -> tuple:
        return self.telegram_id,


class Teacher(BasePerson):
    def __init__(
            self,
            *,
            telegram_id: int,
            full_name: str,
            class_: Optional[list[int]] = None
    ) -> None:
        super().__init__(telegram_id)

        self.full_name = full_name
        self.class_ = class_

    def __call__(self) -> tuple[int, str, list[int] | None]:
        return self.telegram_id, self.full_name, self.class_


class Student(BasePerson):
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

    def __call__(self) -> tuple[int, str, int, list | None, list | None]:
        return self.telegram_id, self.name, self.teacher, self.tasks, self.statistics
