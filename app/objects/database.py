import sqlite3
import json

from .dbobjects import BaseData
from .dbobjects import Teacher
from .dbobjects import Student
from .dbobjects import Task

from .exceptions import UserAlreadyExistsError
from .exceptions import ObjectDoesNotExistError
from .exceptions import UserDoesNotExist
from .exceptions import StudentDoesNotExist
from .exceptions import TeacherDoesNotExist
from .exceptions import TaskDoesNotExist

from ..constants import PATH_TO_DB
from typing import Optional


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
        if not isinstance(data, Task) and self.does_exist(data.telegram_id):
            raise UserAlreadyExistsError()

        if isinstance(data, Teacher):
            self._add_teacher(data)
        elif isinstance(data, Student) and not self.does_teacher_exist(data.teacher):
            raise TeacherDoesNotExist(data.teacher)
        elif isinstance(data, Student):
            self._add_student(data)
        elif isinstance(data, Task):
            self._add_task(data)

        self.connection.commit()

    def give_task_to_student(
            self,
            student_id: int,
            teacher_id: int,
            task_name: str
    ) -> None:
        if not self.does_student_exist(student_id):
            raise ObjectDoesNotExistError(student_id)
        if not self.does_teacher_exist(teacher_id):
            raise ObjectDoesNotExistError(teacher_id)
        if not self.does_task_exist(task_name):
            raise TaskDoesNotExist(task_name)

        task = self.get_task(teacher_id, task_name)
        if task is None:
            raise TaskDoesNotExist(task_name)

        tasks = self.get_student_tasks(student_id)
        current_tasks = json.loads(tasks[0]) if tasks and tasks[0] else []

        new_giving = {
            "title": task.title,
            "description": task.description,
            "level": task.level
        }
        current_tasks.append(new_giving)

        updated_tasks_json = json.dumps(current_tasks)
        self.cursor.execute("""
        UPDATE Students
        SET tasks = ?
        WHERE telegram_id = ?
        """, (updated_tasks_json, student_id))
        self.connection.commit()

    def del_user(
            self,
            id_: int
    ) -> None:
        if not self.does_exist(id_):
            raise ObjectDoesNotExistError(id_)

        table_to_delete_from = "Teachers" if self.does_teacher_exist(id_) else "Students"

        self.cursor.execute(f"""
        DELETE FROM {table_to_delete_from}
        WHERE telegram_id = ?
        """, (id_,))
        self.connection.commit()

    def get_students(
            self,
            teacher_id: int
    ) -> list[Student]:
        if not self.does_teacher_exist(teacher_id):
            raise TeacherDoesNotExist(teacher_id)

        self.cursor.execute("""
        SELECT telegram_id, name, teacher, tasks, statistics
        FROM Students
        WHERE teacher = ?
        """, (teacher_id,))
        students = self.cursor.fetchall()

        return [Student(
            telegram_id=student[0],
            name=student[1],
            teacher=student[2],
            tasks=student[3],
            statistics=student[4]
        ) for student in students]

    def get_teacher_of_student(
            self,
            student_id: int
    ) -> int | None:
        self.cursor.execute("""
        SELECT teacher
        FROM Students
        WHERE telegram_id = ?
        """, (student_id,))
        teacher_id = self.cursor.fetchone()

        if len(teacher_id):
            return int(teacher_id[0])
        return None

    def get_tasks(
            self,
            teacher_id: int
    ) -> list[Task]:
        if not self.does_teacher_exist(teacher_id):
            raise TeacherDoesNotExist(teacher_id)

        self.cursor.execute("""
        SELECT teacher_id, title, description, right_answer, level
        FROM Tasks
        WHERE teacher_id = ?
        """, (teacher_id,))
        tasks = self.cursor.fetchall()

        return [Task(
            telegram_id=task[0],
            title=task[1],
            description=task[2],
            right_answer=task[3],
            level=task[4]
        ) for task in tasks]

    def get_task(
            self,
            teacher_id: int,
            title: str
    ) -> Task | None:
        if not self.does_teacher_exist(teacher_id):
            raise TeacherDoesNotExist(teacher_id)

        self.cursor.execute("""
        SELECT teacher_id, title, description, right_answer, level
        FROM Tasks
        WHERE teacher_id = ? AND title = ?
        """, (teacher_id, title))

        task = self.cursor.fetchone()

        if task is not None:
            return Task(
                telegram_id=task[0],
                title=task[1],
                description=task[2],
                right_answer=task[3],
                level=task[4]
            )

        return None

    def get_student_tasks(
            self,
            student_id: int
    ) -> str:
        # if not self.does_student_exist(student_id):
        #     raise StudentDoesNotExist(student_id)

        self.cursor.execute("""
        SELECT tasks
        FROM Students
        WHERE telegram_id = ? 
        """, (student_id,))
        tasks = self.cursor.fetchone()

        return tasks

    def get_student_tasks_names(
            self,
            student_id: int
    ) -> list[str]:
        tasks = self.get_student_tasks(student_id)

        if tasks:
            tasks = json.loads(tasks[0])
            res = []

            for task in tasks:
                res.append(task["title"])

            return res
        else:
            return []

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

    def does_exist(
            self,
            id_: int
    ) -> bool:
        return self.does_teacher_exist(id_) or self.does_student_exist(id_)

    def does_teacher_exist(
            self,
            id_: int
    ) -> bool:
        self.cursor.execute("""
        SELECT telegram_id 
        FROM Teachers
        WHERE telegram_id = ?
        """, (id_,))

        return bool(self.cursor.fetchone())

    def does_student_exist(
            self,
            id_: int
    ) -> bool:
        self.cursor.execute("""
        SELECT telegram_id 
        FROM Students
        WHERE telegram_id = ?
        """, (id_,))

        return bool(self.cursor.fetchone())

    def does_task_exist(
            self,
            title: str,
            teacher_id: Optional[int] = None
    ) -> bool:
        params_to_insert = [title]

        if teacher_id is not None:
            params_to_insert.append(teacher_id)

        self.cursor.execute(f"""
        SELECT title
        FROM Tasks
        WHERE title = ? {"AND teacher_id = ?" if teacher_id is not None else ""}
        """, tuple(params_to_insert))

        return bool(self.cursor.fetchone())
