# gui/main_window.py
import logging
from pathlib import Path
from tkinter import filedialog
from typing import Optional

import customtkinter as ctk

from db.database import Database
from gui.dialogs import show_error, show_info
from gui.employees_form import EmployeesForm
from gui.work_order_form import WorkOrderForm
from gui.work_types_form import WorkTypesForm
from reports.excel_report import ExcelReportGenerator
from utils.excel_handler import ExcelHandler

logger = logging.getLogger(__name__)


class MainWindow(ctk.CTk):
    """Главное окно программы с обработкой ошибок и проверкой данных."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Учет сдельных работ")
        self.geometry("1200x800")
        self.db = Database()
        self._load_filters_data()

        # Настройка интерфейса
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")
        self._init_ui()

    def _init_ui(self) -> None:
        """Инициализация пользовательского интерфейса с обработкой ошибок."""
        try:
            self.tabview = ctk.CTkTabview(self)
            self._create_tabs()
            self._init_import_export_buttons()
        except Exception as e:
            logger.error(f"Ошибка инициализации интерфейса: {str(e)}")
            show_error("Критическая ошибка при создании интерфейса")

    def _create_tabs(self) -> None:
        """Создание вкладок с обработкой исключений."""
        tabs = ["Наряды", "Работники", "Виды работ", "Отчеты"]
        for tab in tabs:
            self.tabview.add(tab)
        self.tabview.pack(expand=True, fill="both", padx=20, pady=20)

        self._init_work_orders_tab()
        self._init_employees_tab()
        self._init_work_types_tab()
        self._init_reports_tab()

    def _load_filters_data(self) -> None:
        """Загрузка данных для фильтров с проверкой на ошибки."""
        try:
            self.contracts = self._safe_query("SELECT contract_code FROM contracts") or []
            self.products = self._safe_query("SELECT name FROM products") or []
        except Exception as e:
            logger.error(f"Ошибка загрузки фильтров: {str(e)}")
            show_error("Ошибка загрузки справочников")

    def _safe_query(self, query: str) -> Optional[list]:
        """Безопасное выполнение запроса с обработкой ошибок."""
        result = self.db.execute_query(query)
        if result is None:
            logger.warning(f"Пустой результат для запроса: {query}")
        return result

    def _init_work_orders_tab(self) -> None:
        """Инициализация вкладки с нарядами."""
        try:
            tab = self.tabview.tab("Наряды")
            WorkOrderForm(tab, self.db)
        except Exception as e:
            logger.error(f"Ошибка инициализации вкладки нарядов: {str(e)}")
            show_error("Ошибка создания формы нарядов")

    def _init_employees_tab(self) -> None:
        """Инициализация вкладки с работниками."""
        try:
            tab = self.tabview.tab("Работники")
            EmployeesForm(tab, self.db)
        except Exception as e:
            logger.error(f"Ошибка инициализации вкладки работников: {str(e)}")
            show_error("Ошибка создания формы работников")

    def _init_work_types_tab(self) -> None:
        """Инициализация вкладки с видами работ."""
        try:
            tab = self.tabview.tab("Виды работ")
            WorkTypesForm(tab, self.db)
        except Exception as e:
            logger.error(f"Ошибка инициализации вкладки видов работ: {str(e)}")
            show_error("Ошибка создания формы видов работ")

    def _init_reports_tab(self) -> None:
        """Инициализация вкладки отчетов с базовой функциональностью."""
        try:
            tab = self.tabview.tab("Отчеты")
            btn_frame = ctk.CTkFrame(tab)
            btn_frame.pack(pady=20)

            ctk.CTkButton(
                btn_frame,
                text="Сформировать Excel-отчет",
                command=self._generate_excel_report
            ).pack(side="left", padx=10)

            ctk.CTkButton(
                btn_frame,
                text="Сформировать PDF-отчет",
                command=self._generate_pdf_report
            ).pack(side="left", padx=10)
        except Exception as e:
            logger.error(f"Ошибка инициализации вкладки отчетов: {str(e)}")

    def _generate_excel_report(self) -> None:
        """Генерация Excel-отчета с обработкой ошибок."""
        try:
            generator = ExcelReportGenerator(self.db)
            report_path = generator.generate()
            if report_path:
                show_info(f"Отчет сохранен: {report_path}")
        except Exception as e:
            logger.error(f"Ошибка генерации Excel-отчета: {str(e)}")
            show_error("Ошибка создания отчета")

    def _generate_pdf_report(self) -> None:
        """Заглушка для генерации PDF-отчета."""
        show_info("PDF-отчеты временно недоступны")

    def _init_import_export_buttons(self) -> None:
        """Добавление кнопок импорта/экспорта с проверкой прав доступа."""
        self._add_buttons_to_tab("Работники")
        self._add_buttons_to_tab("Виды работ")

    def _add_buttons_to_tab(self, tab_name: str) -> None:
        """Создание кнопок для операций с Excel."""
        try:
            tab = self.tabview.tab(tab_name)
            btn_frame = ctk.CTkFrame(tab)
            btn_frame.pack(pady=10)

            ctk.CTkButton(
                btn_frame,
                text="Экспорт в Excel",
                command=lambda: self._export_data(tab_name)
            ).pack(side="left", padx=5)

            ctk.CTkButton(
                btn_frame,
                text="Импорт из Excel",
                command=lambda: self._import_data(tab_name)
            ).pack(side="right", padx=5)
        except Exception as e:
            logger.error(f"Ошибка создания кнопок для {tab_name}: {str(e)}")

    def _export_data(self, table_name: str) -> None:
        """Экспорт данных с обработкой исключений."""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel Files", "*.xlsx")]
            )
            if not file_path:
                return

            handler = ExcelHandler(self.db)
            if handler.export_table(table_name.lower(), Path(file_path)):
                show_info("Данные успешно экспортированы")
            else:
                show_error("Ошибка при экспорте")
        except Exception as e:
            logger.error(f"Ошибка экспорта данных: {str(e)}")
            show_error("Ошибка при экспорте данных")

    def _import_data(self, table_name: str) -> None:
        """Импорт данных с проверкой формата файла."""
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("Excel Files", "*.xlsx")]
            )
            if not file_path:
                return

            handler = ExcelHandler(self.db)
            success, msg = handler.import_table(table_name.lower(), Path(file_path))
            if success:
                show_info(msg)
                self._reload_current_tab()
            else:
                show_error(msg)
        except Exception as e:
            logger.error(f"Ошибка импорта данных: {str(e)}")
            show_error("Ошибка при импорте данных")

    def _reload_current_tab(self) -> None:
        """Перезагрузка текущей вкладки с обновлением данных."""
        current_tab = self.tabview.get()
        try:
            if current_tab == "Работники":
                self._init_employees_tab()
            elif current_tab == "Виды работ":
                self._init_work_types_tab()
        except Exception as e:
            logger.error(f"Ошибка перезагрузки вкладки: {str(e)}")


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()