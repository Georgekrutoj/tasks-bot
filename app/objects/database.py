import sqlite3

from .dbobjects import BaseData
from .dbobjects import Teacher
from .dbobjects import Student
from .dbobjects import Task

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
            full_name STRING
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
            teacher_id INTEGER,
            title STRING,
            description STRING,
            right_answer STRING,
            level STRING
        )
        """)

        self.connection.commit()

    def add(
            self,
            data: BaseData
    ) -> None:
        if not isinstance(data, Task) and self.is_exist(data.telegram_id):
            raise UserAlreadyExistsError()

        if isinstance(data, Teacher):
            self._add_teacher(data)
        elif isinstance(data, Student) and not self.is_teacher_exist(data.teacher):
            raise UnknownTeacherError(data.teacher)
        elif isinstance(data, Student):
            self._add_student(data)
        elif isinstance(data, Task):
            self._add_task(data)

        self.connection.commit()

    def del_user(
            self,
            id_: int
    ) -> None:
        if not self.is_exist(id_):
            raise UserIsNotExistError(id_)

        table_to_delete_from = "Teachers" if self.is_teacher_exist(id_) else "Students"

        self.cursor.execute(f"""
        DELETE FROM {table_to_delete_from}
        WHERE telegram_id = ?
        """, (id_,))
        self.connection.commit()

    def get_students(
            self,
            teacher_id: int
    ) -> list[Student]:
        if not self.is_teacher_exist(teacher_id):
            raise UnknownTeacherError(teacher_id)

        self.cursor.execute("""
        SELECT *
        FROM Students
        WHERE teacher = ?
        """, (teacher_id,))
        students = self.cursor.fetchall()

        return [Student(
            telegram_id=student[1],
            name=student[2],
            teacher=student[3],
            tasks=student[4],
            statistics=student[5]
        ) for student in students]

    def close(self) -> None:
        self.connection.close()

    def _add_teacher(
            self,
            teacher_data: Teacher
    ) -> None:
        self.cursor.execute("""
        INSERT INTO Teachers (
            telegram_id,
            full_name
        ) VALUES (
            ?,
            ?
        )
        """, teacher_data())

    def _add_student(
            self,
            student_data: Student
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

    def _add_task(
            self,
            task_data: Task
    ) -> None:
        self.cursor.execute("""
        INSERT INTO Tasks (
            teacher_id,
            title,
            description,
            right_answer,
            level
        ) VALUES (
            ?,
            ?,
            ?,
            ?,
            ?
        )
        """, task_data())

    def is_exist(
            self,
            id_: int
    ) -> bool:
        return self.is_teacher_exist(id_) or self.is_student_exist(id_)

    def is_teacher_exist(
            self,
            id_: int
    ) -> bool:
        self.cursor.execute("""
        SELECT telegram_id 
        FROM Teachers
        WHERE telegram_id = ?
        """, (id_,))

        return bool(self.cursor.fetchone())

    def is_student_exist(
            self,
            id_: int
    ) -> bool:
        self.cursor.execute("""
        SELECT telegram_id 
        FROM Students
        WHERE telegram_id = ?
        """, (id_,))

        return bool(self.cursor.fetchone())

    def is_task_exist(
            self,
            title: str
    ) -> bool:
        self.cursor.execute("""
        SELECT title
        FROM Tasks
        WHERE title = ?
        """, (title,))

        return bool(self.cursor.fetchone())
