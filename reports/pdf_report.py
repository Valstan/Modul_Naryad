# reports/pdf_report.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from db.database import Database
from pathlib import Path
from datetime import datetime


class PDFReportGenerator:
    """Генератор отчетов в формате PDF."""

    def __init__(self, db: Database) -> None:
        self.db = db
        self._output_dir = Path("reports/pdf")
        self._output_dir.mkdir(exist_ok=True, parents=True)
        self.styles = getSampleStyleSheet()

    def generate(self, filters: dict = None, filename: str = None) -> str:
        """Генерирует PDF-отчет с фильтрацией данных."""
        try:
            # Запрос данных из БД
            data = self._fetch_data(filters)
            if not data:
                return "Нет данных для отчета."

            # Создание PDF
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"report_{timestamp}.pdf"

            output_path = self._output_dir / filename
            c = canvas.Canvas(str(output_path), pagesize=A4)

            # Заголовок
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, 800, "Отчет по нарядам работ")

            # Таблица с данными
            table = Table(data, colWidths=[100, 80, 120, 100, 80])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black)
            ]))

            # Размещение таблицы на странице
            table.wrapOn(c, 400, 600)
            table.drawOn(c, 50, 650)

            c.save()
            return str(output_path)

        except Exception as e:
            return f"Ошибка: {str(e)}"

    def _fetch_data(self, filters: dict) -> list:
        """Возвращает данные для отчета с учетом фильтров."""
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

        # Заголовки таблицы
        data = [["Наряд №", "Дата", "Изделие", "Контракт", "Сумма"]]
        for row in raw_data:
            data.append([str(item) for item in row])

        return data