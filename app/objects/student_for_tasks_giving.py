class StudentForTasksGiving:
    def __init__(
            self,
            name: str,
            telegram_id: int
    ) -> None:
        self.name = name
        self.telegram_id = telegram_id

    def __str__(self) -> str:
        return self.name
