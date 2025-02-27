class UserAlreadyExistsError(Exception):
    def __init__(
            self,
            message: str = "the same user already exists",
            /
    ) -> None:
        super().__init__(message)


class ObjectDoesNotExistError(Exception):
    def __init__(
            self,
            id_: int | str = None,  # Can be int (id) or str (for tasks names)
            message: str = "cannot find object with this ID in database: ",
            /
    ) -> None:
        super().__init__(message + str(id_))


class UserDoesNotExist(ObjectDoesNotExistError):
    def __init__(
            self,
            id_: int = None,
            /
    ) -> None:
        super().__init__(id_, "cannot find user with this ID: ")


class StudentDoesNotExist(ObjectDoesNotExistError):
    def __init__(
            self,
            id_: int,
            /
    ) -> None:
        super().__init__(id_, "cannot find student with this ID: ")


class TeacherDoesNotExist(ObjectDoesNotExistError):
    def __init__(
            self,
            id_: int = None,
            /
    ) -> None:
        super().__init__(id_, "cannot find teacher with this ID: ")


class TaskDoesNotExist(ObjectDoesNotExistError):
    def __init__(
            self,
            name: str = None,
            /
    ) -> None:
        super().__init__(name, "cannot find task with this name: ")
