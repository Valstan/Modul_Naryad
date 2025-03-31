# db/database.py
import logging
import sqlite3
from pathlib import Path
from typing import Optional, List, Tuple, Any

logger = logging.getLogger(__name__)


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
            try:
                cursor.executescript(sql)
                self.conn.commit()
            except sqlite3.Error as e:
                logger.error(f"Ошибка создания таблиц: {str(e)}")
                self.conn.rollback()
            finally:
                cursor.close()

    def execute_query(
            self,
            query: str,
            params: Optional[Tuple[Any, ...]] = None
    ) -> Optional[List[Tuple[Any, ...]]]:
        """
        Безопасное выполнение SQL-запроса с поддержкой транзакций.

        Returns:
            Список кортежей с результатами запроса или None при ошибке.
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("BEGIN TRANSACTION")
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            self.conn.commit()
            return result
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Ошибка выполнения запроса: {str(e)}")
            return None  # Явный возврат None при ошибке
        finally:
            cursor.close()

    def __del__(self) -> None:
        """Закрытие соединения при удалении объекта."""
        if hasattr(self, "conn"):
            self.conn.close()