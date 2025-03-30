# gui/main_window.py
from typing import Dict

import customtkinter as ctk

from db.database import Database
from gui.dialogs import show_error, show_info
from gui.employees_form import EmployeesForm
from gui.work_order_form import WorkOrderForm
from reports.excel_report import ExcelReportGenerator


class MainWindow(ctk.CTk):
    """Главное окно программы с вкладками для управления данными."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Учет сдельных работ")
        self.geometry("1200x800")

        # Инициализация БД
        self.db: Database = Database()
        self._load_filters_data()

        # Стиль интерфейса
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

        # Создание вкладок
        self.tabview = ctk.CTkTabview(self)
        self.tabview.add("Наряды")
        self.tabview.add("Работники")
        self.tabview.add("Отчеты")
        self.tabview.pack(expand=True, fill="both", padx=20, pady=20)

        # Загрузка содержимого вкладок
        self._init_work_orders_tab()
        self._init_employees_tab()
        self._init_reports_tab()

    def _load_filters_data(self) -> None:
        """Загрузка данных для фильтров отчетов."""
        self.contracts = self.db.execute_query("SELECT contract_code FROM contracts")
        self.products = self.db.execute_query("SELECT name FROM products")

    def _init_work_orders_tab(self) -> None:
        """Инициализация вкладки 'Наряды'."""
        tab = self.tabview.tab("Наряды")
        WorkOrderForm(tab, self.db)

    def _init_employees_tab(self) -> None:
        """Инициализация вкладки 'Работники'."""
        tab = self.tabview.tab("Работники")
        EmployeesForm(tab, self.db)

    def _init_reports_tab(self) -> None:
        """Инициализация вкладки 'Отчеты'."""
        tab = self.tabview.tab("Отчеты")

        # Фрейм для фильтров
        filters_frame = ctk.CTkFrame(tab)
        filters_frame.pack(side="left", fill="y", padx=10, pady=10)

        # Поля фильтров
        ctk.CTkLabel(filters_frame, text="Фильтры отчетов", font=("Arial", 14)).pack(pady=5)

        # Дата начала
        self.start_date_entry = ctk.CTkEntry(filters_frame, placeholder_text="Дата начала (ДД.ММ.ГГГГ)")
        self.start_date_entry.pack(pady=5)

        # Дата окончания
        self.end_date_entry = ctk.CTkEntry(filters_frame, placeholder_text="Дата окончания (ДД.ММ.ГГГГ)")
        self.end_date_entry.pack(pady=5)

        # Контракты
        self.contract_combobox = ctk.CTkComboBox(
            filters_frame,
            values=[c[0] for c in self.contracts],
            placeholder_text="Выберите контракт"
        )
        self.contract_combobox.pack(pady=5)

        # Изделия
        self.product_combobox = ctk.CTkComboBox(
            filters_frame,
            values=[p[0] for p in self.products],
            placeholder_text="Выберите изделие"
        )
        self.product_combobox.pack(pady=5)

        # Фрейм для кнопок экспорта
        export_frame = ctk.CTkFrame(tab)
        export_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(export_frame, text="Экспорт отчетов", font=("Arial", 14)).pack(pady=10)

        # Кнопки
        ctk.CTkButton(export_frame, text="Excel", command=self._export_excel).pack(pady=5, fill="x")
        ctk.CTkButton(export_frame, text="PDF", command=self._export_pdf).pack(pady=5, fill="x")
        ctk.CTkButton(export_frame, text="HTML", command=self._export_html).pack(pady=5, fill="x")

    def _get_filters(self) -> Dict:
        """Возвращает параметры фильтрации."""
        return {
            "start_date": self.start_date_entry.get(),
            "end_date": self.end_date_entry.get(),
            "contract_code": self.contract_combobox.get(),
            "product": self.product_combobox.get()
        }

    def _export_excel(self) -> None:
        """Экспорт отчета в Excel."""
        try:
            generator = ExcelReportGenerator(self.db)
            path = generator.generate(self._get_filters())
            show_info(f"Excel-отчет сохранен:\n{path}")
        except Exception as e:
            show_error(f"Ошибка: {str(e)}")

    def _export_pdf(self) -> None:
        """Экспорт отчета в PDF."""
        try:
            from reports.pdf_report import PDFReportGenerator
            generator = PDFReportGenerator(self.db)
            path = generator.generate(self._get_filters())
            if path.startswith("Ошибка"):
                show_error(path)
            else:
                show_info(f"PDF-отчет сохранен:\n{path}")
        except Exception as e:
            show_error(f"Ошибка: {str(e)}")

    def _export_html(self) -> None:
        """Экспорт отчета в HTML."""
        try:
            from reports.html_report import HTMLReportGenerator
            generator = HTMLReportGenerator(self.db)
            path = generator.generate(self._get_filters())
            if path.startswith("Ошибка"):
                show_error(path)
            else:
                show_info(f"HTML-отчет сохранен:\n{path}")
        except Exception as e:
            show_error(f"Ошибка: {str(e)}")


if __name__ == "__main__":
    try:
        app = MainWindow()
        app.mainloop()
    except Exception as e:
        show_error(f"Ошибка запуска: {str(e)}")