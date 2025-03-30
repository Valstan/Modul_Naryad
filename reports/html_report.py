# reports/html_report.py
from db.database import Database
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

class HTMLReportGenerator:
    """Генератор отчетов в формате HTML."""

    def __init__(self, db: Database) -> None:
        self.db = db
        self._output_dir = Path("reports/html")
        self._output_dir.mkdir(exist_ok=True, parents=True)

    def generate(self, filters: Optional[Dict] = None, filename: Optional[str] = None) -> str:
        """Генерирует HTML-отчет с фильтрацией данных."""
        try:
            data = self._fetch_data(filters)
            if not data:
                return "Нет данных для отчета."

            # Формирование HTML-таблицы
            html_content = [
                "<!DOCTYPE html>",
                "<html>",
                "<head>",
                "<title>Отчет по нарядам</title>",
                "<style>",
                "table { border-collapse: collapse; width: 100%; }",
                "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
                "th { background-color: #f2f2f2; }",
                "</style>",
                "</head>",
                "<body>",
                "<h1>Отчет по нарядам работ</h1>",
                "<table>",
                "<tr><th>Наряд №</th><th>Дата</th><th>Изделие</th><th>Контракт</th><th>Сумма</th></tr>"
            ]

            for row in data:
                html_content.append(f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td></tr>")

            html_content.extend(["</table>", "</body>", "</html>"])

            # Сохранение файла
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"report_{timestamp}.html"

            output_path = self._output_dir / filename
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(html_content))

            return str(output_path)

        except Exception as e:
            return f"Ошибка: {str(e)}"

    def _fetch_data(self, filters: Optional[Dict]) -> list:
        """Загружает данные из БД с учетом фильтров."""
        query = """  
            SELECT  
                wo.id AS order_id,  
                wo.order_date,  
                p.name AS product,  
                c.contract_code,  
                SUM(owt.amount) AS total_amount  
            FROM work_orders wo  
            LEFT JOIN products p ON wo.product_id = p.id  
            LEFT JOIN contracts c ON wo.contract_id = c.id  
            LEFT JOIN order_work_types owt ON wo.id = owt.order_id  
            GROUP BY wo.id  
        """
        raw_data = self.db.execute_query(query)
        return raw_data