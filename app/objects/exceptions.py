class UserAlreadyExistsError(Exception):
    def __init__(
            self,
            message: str = "the same user already exists",
            /
    ) -> None:
        super().__init__(message)


class UserDoesNotExistError(Exception):
    def __init__(
            self,
            id_: int = None,
            message: str = "cannot find user with this ID: ",
            /
    ) -> None:
        super().__init__(message + str(id_))


class UnknownTeacherError(UserDoesNotExistError):
    def __init__(
            self,
            id_: int = None,
            /
    ) -> None:
        super().__init__(id_)
