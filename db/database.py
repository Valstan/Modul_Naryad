# db/database.py
import sqlite3
from pathlib import Path
from typing import Optional, List, Tuple

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_db()
        return cls._instance

    def _init_db(self) -> None:
        """Инициализация БД с автоматическим созданием файла."""
        self.db_path = Path("work_orders.db")
        self.db_path.touch(exist_ok=True)  # Создать файл, если его нет
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self) -> None:
        """Создание таблиц из SQL-файла."""
        sql_file = Path(__file__).parent / "queries.sql"
        if sql_file.exists():
            with open(sql_file, "r") as f:
                sql = f.read()
            self.cursor.executescript(sql)
            self.conn.commit()

    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Tuple]:
        """Безопасное выполнение SQL-запроса."""
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        self.conn.commit()
        return self.cursor.fetchall()

    def __del__(self) -> None:
        """Закрытие соединения при удалении объекта."""
        self.conn.close()