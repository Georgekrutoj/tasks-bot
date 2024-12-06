import sqlite3

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
            id INTEGER PRIMARY KEY,
        )
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Students (
            id INTEGER,
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
            id INTEGER,
            title STRING,
            text STRING,
            level STRING
        )
        """)

        self.connection.commit()
        self.connection.close()
