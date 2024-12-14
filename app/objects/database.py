import sqlite3

from .persons import BasePerson
from .persons import Teacher
from .persons import Student

from .exceptions import UserAlreadyExistsError
from .exceptions import UserIsNotExistError
from .exceptions import UnknownTeacherError

from ..constants import PATH_TO_DB


class Tasks:
    def __init__(
            self,
            path: str = PATH_TO_DB
    ) -> None:
        self.path = path
        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            full_name STRING,
            class STRING
        )
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            name STRING,
            teacher INTEGER,
            tasks STRING,
            statistics STRING,
            FOREIGN KEY (teacher) REFERENCES Teachers(id)
        )
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title STRING,
            text STRING,
            level STRING
        )
        """)

        self.connection.commit()

    def add(
            self,
            data: BasePerson
    ) -> None:
        if self._is_exist(data):
            raise UserAlreadyExistsError()
        elif isinstance(data, Teacher):
            self._add_teacher(data)
        elif isinstance(data, Student) and not self._is_teacher_exist(data.teacher):
            raise UnknownTeacherError(data.teacher)
        else:
            self._add_student(data)

        self.connection.commit()

    def del_user(
            self,
            id_: int
    ) -> None:
        if not self._is_exist(BasePerson(id_)):
            raise UserIsNotExistError(id_)

    def close(self) -> None:
        self.connection.close()

    def _add_teacher(
            self,
            teacher_data: Teacher,
            /
    ) -> None:
        self.cursor.execute("""
        INSERT INTO Teachers (
            telegram_id,
            full_name,
            class
        ) VALUES (
            ?,
            ?,
            ?
        )
        """, teacher_data())

    def _add_student(
            self,
            student_data: Student,
            /
    ) -> None:
        self.cursor.execute("""
        INSERT INTO Students (
            telegram_id,
            name,
            teacher,
            tasks,
            statistics
        ) VALUES (
            ?,
            ?,
            ?,
            ?,
            ?
        )
        """, student_data())

    def _is_exist(
            self,
            data: BasePerson
    ) -> bool:
        self.cursor.execute("""
        SELECT telegram_id 
        FROM Teachers
        WHERE telegram_id = ?
        UNION
        SELECT telegram_id
        FROM Students
        WHERE telegram_id = ?
        """, (data.telegram_id, data.telegram_id))

        return bool(self.cursor.fetchone())

    def _is_teacher_exist(
            self,
            id_: int
    ) -> bool:
        self.cursor.execute("""
        SELECT telegram_id 
        FROM Teachers
        WHERE telegram_id = ?
        """, (id_,))

        return bool(self.cursor.fetchone())
