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
    """Главное окно программы."""

    def __init__(self, db: Database) -> None:
        super().__init__()
        self.title("Учет сдельных работ")
        self.geometry("1200x800")
        self.db = db

        try:
            logger.info("Инициализация главного окна")
            self._configure_theme()
            self._init_ui()
            self._load_filters_data()
        except Exception as e:
            logger.critical(f"Ошибка инициализации: {str(e)}", exc_info=True)
            show_error("Не удалось запустить приложение")
            raise

    def _configure_theme(self) -> None:
        """Настройка темы интерфейса."""
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

    def _init_ui(self) -> None:
        """Инициализация интерфейса."""
        self.tabview = ctk.CTkTabview(self)
        self.tabview.add("Наряды")
        self.tabview.add("Работники")
        self.tabview.add("Виды работ")
        self.tabview.add("Отчеты")
        self.tabview.pack(expand=True, fill="both", padx=20, pady=20)

        # Инициализация вкладок
        self._init_work_orders_tab()
        self._init_employees_tab()
        self._init_work_types_tab()
        self._init_reports_tab()

    def _init_work_orders_tab(self) -> None:
        """Инициализация вкладки с нарядами."""
        tab = self.tabview.tab("Наряды")
        WorkOrderForm(tab, self.db)

    def _init_employees_tab(self) -> None:
        """Инициализация вкладки с работниками."""
        tab = self.tabview.tab("Работники")
        EmployeesForm(tab, self.db)

    def _init_work_types_tab(self) -> None:
        """Инициализация вкладки с видами работ."""
        tab = self.tabview.tab("Виды работ")
        WorkTypesForm(tab, self.db)

    def _init_reports_tab(self) -> None:
        """Инициализация вкладки отчетов."""
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

    def _load_filters_data(self) -> None:
        """Загрузка данных для фильтров."""
        self.contracts = self.db.execute_query("SELECT contract_code FROM contracts") or []
        self.products = self.db.execute_query("SELECT name FROM products") or []

    def _generate_excel_report(self) -> None:
        """Генерация Excel-отчета."""
        try:
            generator = ExcelReportGenerator(self.db)
            report_path = generator.generate()
            if report_path:
                show_info(f"Отчет сохранен: {report_path}")
        except Exception as e:
            logger.error(f"Ошибка генерации отчета: {str(e)}")
            show_error("Ошибка создания отчета")

    def _generate_pdf_report(self) -> None:
        """Заглушка для генерации PDF-отчета."""
        show_info("PDF-отчеты временно недоступны")

    def __del__(self) -> None:
        """Завершение работы."""
        if hasattr(self, "db"):
            self.db.conn.close()