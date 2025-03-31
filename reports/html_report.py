# reports/html_report.py
from pathlib import Path
from datetime import datetime
from db.database import Database
from db.queries import WORK_ORDERS_FOR_PDF_HTML
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class HTMLReportGenerator:
    """Генератор отчетов в формате HTML."""

    def __init__(self, db: Database) -> None:
        self.db = db
        self._output_dir = Path("reports/html")
        self._output_dir.mkdir(exist_ok=True, parents=True)

    def generate(self, filters: Optional[Dict] = None, filename: Optional[str] = None) -> Optional[str]:
        """Генерирует HTML-отчет."""
        try:
            data = self.db.execute_query(WORK_ORDERS_FOR_PDF_HTML)
            if not data:
                logger.warning("Нет данных для отчета")
                return None

            # Формирование HTML-контента
            html_content = self._build_html(data)

            # Сохранение файла
            output_path = self._get_output_path(filename)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            return str(output_path)

        except Exception as e:
            logger.error(f"Ошибка генерации HTML-отчета: {str(e)}")
            return None

    def _build_html(self, data: list) -> str:
        """Создает HTML-структуру."""
        # Реализация построения HTML...
        return "<html>...</html>"

    def _get_output_path(self, filename: Optional[str]) -> Path:
        """Генерирует путь к файлу."""
        if filename:
            return self._output_dir / filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self._output_dir / f"report_{timestamp}.html"