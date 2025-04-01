# reports/excel_report.py
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

import pandas as pd

from db.database import Database
from db.queries import REPORT_BASE_QUERY

logger = logging.getLogger(__name__)


class ExcelReportGenerator:
    """Генератор отчетов в формате Excel."""

    def __init__(self, db: Database) -> None:
        self.db = db
        self._output_dir = Path("reports/excel")
        self._output_dir.mkdir(exist_ok=True, parents=True)

    def generate(
            self,
            filters: Optional[Dict] = None,
            filename: Optional[str] = None
    ) -> Optional[str]:
        """Генерирует отчет с фильтрацией данных."""
        try:
            # Выполнение запроса
            data = self.db.execute_query(REPORT_BASE_QUERY)
            if not data:
                logger.warning("Нет данных для отчета")
                return None

            # Создание DataFrame
            df = pd.DataFrame(
                data,
                columns=["order_id", "order_date", "product", "contract_code",
                         "total_amount", "workers"]
            )

            # Применение фильтров
            if filters:
                df = self._apply_filters(df, filters)
                if df.empty:
                    logger.warning("Данные не соответствуют фильтрам")
                    return None

            # Генерация имени файла
            output_path = self._get_output_path(filename)
            df.to_excel(output_path, index=False, engine="openpyxl")
            return str(output_path)

        except Exception as e:
            logger.error(f"Ошибка генерации Excel-отчета: {str(e)}", exc_info=True)
            return None

    def _apply_filters(self, df: pd.DataFrame, filters: Dict) -> pd.DataFrame:
        """Применяет фильтры к данным."""
        for column, value in filters.items():
            if column not in df.columns:
                continue

            if isinstance(value, (list, tuple)):
                df = df[df[column].isin(value)]
            elif isinstance(value, dict):
                # Для диапазонов значений (например, дат)
                if "start" in value and "end" in value:
                    df = df[df[column].between(value["start"], value["end"])]
            else:
                df = df[df[column] == value]

        return df

    def _get_output_path(self, filename: Optional[str]) -> Path:
        """Генерирует путь к файлу."""
        if filename:
            if not filename.endswith(".xlsx"):
                filename += ".xlsx"
            return self._output_dir / filename

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self._output_dir / f"report_{timestamp}.xlsx"