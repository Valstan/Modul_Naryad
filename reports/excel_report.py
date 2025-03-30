# reports/excel_report.py
import pandas as pd
from db.database import Database
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime


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
    ) -> str:
        """Генерирует отчет с фильтрацией данных."""
        query = """
            SELECT 
                wo.id AS order_id,
                wo.order_date,
                p.name AS product,
                c.contract_code,
                SUM(owt.amount) AS total_amount,
                GROUP_CONCAT(e.full_name, ', ') AS workers
            FROM work_orders wo
            LEFT JOIN products p ON wo.product_id = p.id
            LEFT JOIN contracts c ON wo.contract_id = c.id
            LEFT JOIN order_workers ow ON wo.id = ow.order_id
            LEFT JOIN employees e ON ow.worker_id = e.id
            LEFT JOIN order_work_types owt ON wo.id = owt.order_id
            GROUP BY wo.id
        """
        data = self.db.execute_query(query)

        # Преобразование в DataFrame
        df = pd.DataFrame(
            data,
            columns=["order_id", "order_date", "product", "contract_code", "total_amount", "workers"]
        )

        # Применение фильтров
        if filters:
            df = self._apply_filters(df, filters)

        # Генерация имени файла
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{timestamp}.xlsx"

        # Сохранение в Excel
        output_path = self._output_dir / filename
        df.to_excel(output_path, index=False)
        return str(output_path)

    def _apply_filters(self, df: pd.DataFrame, filters: Dict) -> pd.DataFrame:
        """Применяет фильтры к данным."""
        if "start_date" in filters:
            df = df[df["order_date"] >= filters["start_date"]]
        if "contract_code" in filters:
            df = df[df["contract_code"] == filters["contract_code"]]
        # Добавьте другие фильтры по аналогии
        return df