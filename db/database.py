# db/database.py
import sqlite3
from pathlib import Path
from typing import Optional, List, Tuple

class Database:
    """Singleton для управления подключением к SQLite."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_db()
        return cls._instance

    def _init_db(self) -> None:
        """Инициализация БД с автоматическим созданием файла."""
        self.db_path = Path("work_orders.db")
        self.db_path.touch(exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._create_tables()

    def _create_tables(self) -> None:
        """Создание таблиц из SQL-файла."""
        sql_file = Path(__file__).parent / "queries.sql"
        if sql_file.exists():
            with open(sql_file, "r") as f:
                sql = f.read()
            cursor = self.conn.cursor()
            cursor.executescript(sql)
            self.conn.commit()
            cursor.close()

    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Tuple]:
        """Безопасное выполнение SQL-запроса с поддержкой транзакций."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("BEGIN TRANSACTION")
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.conn.commit()
            return cursor.fetchall()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Ошибка БД: {str(e)}")
        finally:
            cursor.close()

    def __del__(self) -> None:
        """Закрытие соединения при удалении объекта."""
        self.conn.close()