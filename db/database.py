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
        """Инициализация БД с автоматическим созданием файла и таблиц."""
        self.db_path = Path("work_orders.db")
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._create_tables()

    def _create_tables(self) -> None:
        """Создание таблиц при первом запуске."""
        tables = [
            """CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                employee_id TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                workshop_number INTEGER NOT NULL,
                position TEXT NOT NULL
            )""",

            """CREATE TABLE IF NOT EXISTS work_types (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                unit TEXT NOT NULL,
                price REAL NOT NULL CHECK(price > 0)
            )""",

            """CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                product_code TEXT UNIQUE NOT NULL
            )""",

            """CREATE TABLE IF NOT EXISTS contracts (
                id INTEGER PRIMARY KEY,
                contract_code TEXT UNIQUE NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                description TEXT
            )""",

            """CREATE TABLE IF NOT EXISTS work_orders (
                id INTEGER PRIMARY KEY,
                order_date TEXT NOT NULL,
                product_id INTEGER NOT NULL,
                contract_id INTEGER NOT NULL,
                total_amount REAL NOT NULL,
                FOREIGN KEY(product_id) REFERENCES products(id),
                FOREIGN KEY(contract_id) REFERENCES contracts(id)
            )""",

            """CREATE TABLE IF NOT EXISTS order_workers (
                order_id INTEGER NOT NULL,
                worker_id INTEGER NOT NULL,
                PRIMARY KEY(order_id, worker_id),
                FOREIGN KEY(order_id) REFERENCES work_orders(id),
                FOREIGN KEY(worker_id) REFERENCES employees(id)
            )""",

            """CREATE TABLE IF NOT EXISTS order_work_types (
                order_id INTEGER NOT NULL,
                work_type_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                amount REAL NOT NULL,
                PRIMARY KEY(order_id, work_type_id),
                FOREIGN KEY(order_id) REFERENCES work_orders(id),
                FOREIGN KEY(work_type_id) REFERENCES work_types(id)
            )"""
        ]

        cursor = self.conn.cursor()
        try:
            for table in tables:
                cursor.execute(table)
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
        """Безопасное выполнение SQL-запроса с поддержкой транзакций."""
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
            return None
        finally:
            cursor.close()

    def __del__(self) -> None:
        """Закрытие соединения при удалении объекта."""
        if hasattr(self, "conn"):
            self.conn.close()

    # Добавление индексов
    def _create_indexes(self):
        """Создание индексов для оптимизации запросов"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_orders_date ON work_orders(order_date)",
            "CREATE INDEX IF NOT EXISTS idx_workers_name ON employees(full_name)",
            "CREATE INDEX IF NOT EXISTS idx_contracts_code ON contracts(contract_code)"
        ]

        cursor = self.conn.cursor()
        try:
            for index in indexes:
                cursor.execute(index)
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Ошибка создания индексов: {str(e)}")