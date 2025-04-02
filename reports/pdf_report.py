# reports/pdf_report.py
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)
from db.database import Database
from db.queries import WORK_ORDERS_FOR_PDF_HTML
from utils.validators import validate_date_range

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """Генератор PDF-отчетов с расширенными возможностями фильтрации."""

    def __init__(self, db: Database):
        self.db = db
        self._output_dir = Path("reports/pdf")
        self._output_dir.mkdir(exist_ok=True, parents=True)
        self.styles = self._create_custom_styles()

    def generate(
            self,
            filters: Optional[Dict] = None,
            filename: Optional[str] = None
    ) -> Optional[str]:
        """Генерирует PDF-отчет с применением фильтров."""
        try:
            data = self._get_filtered_data(filters)
            if not data:
                logger.warning("Нет данных для формирования отчета")
                return None

            output_path = self._get_output_path(filename)
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=A4,
                leftMargin=2 * cm,
                rightMargin=2 * cm
            )
            elements = []
            self._add_header(elements)
            self._add_filters_info(elements, filters)
            self._add_data_table(elements, data)
            self._add_footer(elements)
            doc.build(elements)
            return str(output_path)
        except Exception as e:
            logger.error(f"Ошибка генерации PDF: {str(e)}")
            return None

    def _get_filtered_data(self, filters: Optional[Dict]) -> List[Tuple]:
        """Получение данных с применением фильтров."""
        query = WORK_ORDERS_FOR_PDF_HTML
        params = []
        if filters:
            where_clauses = []
            for key, value in filters.items():
                if value:
                    if key == "date_range":
                        if validate_date_range(value["start"], value["end"]):
                            where_clauses.append(
                                "wo.order_date BETWEEN ? AND ?"
                            )
                            params.extend([value["start"], value["end"]])
                    elif key == "contract":
                        where_clauses.append("c.contract_code = ?")
                        params.append(value)
                    elif key == "product":
                        where_clauses.append("p.name = ?")
                        params.append(value)
                    elif key == "worker":
                        where_clauses.append("e.full_name LIKE ?")
                        params.append(f"%{value}%")
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

        return self.db.execute_query(query, tuple(params)) or []

    def _create_custom_styles(self) -> Dict:
        """Создание кастомных стилей для отчета."""
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name="Title",
            fontSize=14,
            leading=16,
            alignment=1,
            spaceAfter=12
        ))
        styles.add(ParagraphStyle(
            name="Footer",
            fontSize=8,
            textColor=colors.grey,
            alignment=2
        ))
        return styles

    def _add_header(self, elements: List) -> None:
        """Добавление заголовка отчета."""
        title = Paragraph(
            "Отчет по нарядам работ",
            self.styles["Title"]
        )
        elements.append(title)
        elements.append(Spacer(1, 0.5 * cm))

    def _add_filters_info(self, elements: List, filters: Dict) -> None:
        """Добавление информации о примененных фильтрах."""
        if filters:
            filter_text = "Примененные фильтры: " + ", ".join(
                [f"{k}: {v}" for k, v in filters.items() if v]
            )
            elements.append(Paragraph(filter_text, self.styles["Normal"]))
            elements.append(Spacer(1, 0.2 * cm))

    def _add_data_table(self, elements: List, data: List[Tuple]) -> None:
        """Создание основной таблицы с данными."""
        headers = [
            "Наряд №",
            "Дата",
            "Изделие",
            "Контракт",
            "Сумма",
            "Рабочие"
        ]
        table_data = [headers]
        for row in data:
            formatted_row = [
                str(row[0]),
                datetime.strptime(row[1], "%Y-%m-%d").strftime("%d.%m.%Y"),
                row[2] if row[2] else "Не указано",
                row[3] if row[3] else "Без контракта",
                f"{row[4]:,.2f} ₽".replace(",", " "),
                ", ".join(row[5].split(", ")) if row[5] else "Не выбраны"
            ]
            table_data.append(formatted_row)

        table = Table(
            table_data,
            colWidths=[2 * cm, 2.5 * cm, 4 * cm, 4 * cm, 3 * cm, 6 * cm],
            repeatRows=1
        )
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(table)

    def _add_footer(self, elements: List) -> None:
        """Добавление подвала отчета."""
        footer_text = Paragraph(
            f"Сформировано: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
            self.styles["Footer"]
        )
        elements.append(Spacer(1, 1 * cm))
        elements.append(footer_text)

    def _get_output_path(self, filename: Optional[str]) -> Path:
        """Генерация пути для сохранения файла."""
        if filename:
            return self._output_dir / filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self._output_dir / f"report_{timestamp}.pdf"