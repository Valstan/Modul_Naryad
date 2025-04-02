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
    """Главное окно программы с исправленными вкладками."""
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
        """Инициализация интерфейса с исправленными вкладками."""
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both", padx=20, pady=20)

        # Добавляем вкладки с содержимым
        self._init_work_orders_tab()
        self._init_employees_tab()
        self._init_work_types_tab()
        self._init_reports_tab()

    def _init_work_orders_tab(self) -> None:
        """Вкладка нарядов с активным интерфейсом."""
        tab = self.tabview.add("Наряды")
        self.work_order_form = WorkOrderForm(tab, self.db)  # Инициализация формы нарядов

    def _init_employees_tab(self) -> None:
        """Вкладка работников с активным интерфейсом."""
        tab = self.tabview.add("Работники")
        self.employees_form = EmployeesForm(tab, self.db)  # Инициализация формы работников

    def _init_work_types_tab(self) -> None:
        """Вкладка видов работ с активным интерфейсом."""
        tab = self.tabview.add("Виды работ")
        self.work_types_form = WorkTypesForm(tab, self.db)  # Инициализация формы видов работ

    def _init_reports_tab(self) -> None:
        """Вкладка отчетов с функциональными кнопками."""
        tab = self.tabview.add("Отчеты")
        btn_frame = ctk.CTkFrame(tab)
        btn_frame.pack(pady=20)

        # Кнопки генерации отчетов
        ctk.CTkButton(
            btn_frame,
            text="Excel-отчет",
            command=self._generate_excel_report
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="PDF-отчет",
            command=self._generate_pdf_report
        ).pack(side="left", padx=10)

    def _generate_excel_report(self) -> None:
        """Генерация Excel-отчета с проверкой данных."""
        try:
            generator = ExcelReportGenerator(self.db)
            report_path = generator.generate()
            if report_path:
                show_info(f"Отчет сохранен: {report_path}")
        except Exception as e:
            logger.error(f"Ошибка генерации Excel: {str(e)}")
            show_error("Ошибка создания отчета")

    def _generate_pdf_report(self) -> None:
        """Генерация PDF-отчета."""
        show_info("PDF-отчеты временно недоступны. Используйте Excel.")

    def _load_filters_data(self) -> None:
        """Загрузка данных для фильтров (исправлено)."""
        try:
            self.contracts = self.db.execute_query("SELECT contract_code FROM contracts") or []
            self.products = self.db.execute_query("SELECT name FROM products") or []
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {str(e)}")
            show_error("Ошибка загрузки справочников")

    def __del__(self) -> None:
        """Закрытие соединения с БД."""
        if hasattr(self, "db"):
            self.db.conn.close()