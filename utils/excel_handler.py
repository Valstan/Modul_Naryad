# utils/excel_handler.py
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict
from db.database import Database
import logging

logger = logging.getLogger(__name__)


class ExcelHandler:
    """Класс для импорта/экспорта данных из Excel."""

    def __init__(self, db: Database):
        self.db = db
        self.supported_tables = {
            "employees": ("ФИО", "Номер цеха", "Должность", "Табельный номер"),
            "work_types": ("Наименование", "Единица измерения", "Цена")
        }

    def export_table(self, table_name: str, output_path: Path) -> bool:
        """Экспорт таблицы БД в Excel."""
        if table_name not in self.supported_tables:
            logger.error(f"Таблица {table_name} не поддерживается")
            return False

        try:
            data = self.db.execute_query(f"SELECT * FROM {table_name}")
            if not data:
                return False

            df = pd.DataFrame(data, columns=self.supported_tables[table_name])
            df.to_excel(output_path, index=False)
            return True

        except Exception as e:
            logger.error(f"Ошибка экспорта: {str(e)}")
            return False

    def import_table(self, table_name: str, file_path: Path) -> tuple[bool, str]:
        """Импорт данных из Excel в БД."""
        if table_name not in self.supported_tables:
            return (False, f"Таблица {table_name} не поддерживается")

        try:
            df = pd.read_excel(file_path)
            if not self._validate_columns(df, table_name):
                return (False, "Неверная структура файла")

            # Валидация и преобразование данных
            for _, row in df.iterrows():
                self._process_row(table_name, row)

            return (True, "Успешный импорт")

        except Exception as e:
            return (False, f"Ошибка: {str(e)}")

    def _validate_columns(self, df: pd.DataFrame, table_name: str) -> bool:
        """Проверяет соответствие столбцов."""
        expected = set(self.supported_tables[table_name])
        actual = set(df.columns)
        return expected == actual

    def _process_row(self, table_name: str, row: pd.Series) -> None:
        """Обрабатывает строку данных."""
        # Пример для таблицы работников
        if table_name == "employees":
            self.db.execute_query(
                """INSERT INTO employees (full_name, workshop_number, position, employee_id)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(employee_id) DO NOTHING""",
                (row["ФИО"], row["Номер цеха"], row["Должность"], row["Табельный номер"])
            )