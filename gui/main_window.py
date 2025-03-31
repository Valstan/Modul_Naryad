# gui/main_window.py
from tkinter import filedialog
from typing import Dict, Optional
import customtkinter as ctk
from db.database import Database
from gui.dialogs import show_error, show_info
from gui.employees_form import EmployeesForm
from gui.work_order_form import WorkOrderForm
from gui.work_types_form import WorkTypesForm
from reports.excel_report import ExcelReportGenerator
from utils.excel_handler import ExcelHandler


class MainWindow(ctk.CTk):
    """Главное окно программы."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Учет сдельных работ")
        self.geometry("1200x800")
        self.db = Database()
        self._load_filters_data()

        # Настройка интерфейса
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

        # Создание вкладок
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
        self._init_import_export_buttons()

    def _load_filters_data(self) -> None:
        """Загрузка данных для фильтров."""
        self.contracts = self.db.execute_query("SELECT contract_code FROM contracts") or []
        self.products = self.db.execute_query("SELECT name FROM products") or []

    def _init_work_orders_tab(self) -> None:
        """Вкладка 'Наряды'."""
        tab = self.tabview.tab("Наряды")
        WorkOrderForm(tab, self.db)

    def _init_employees_tab(self) -> None:
        """Вкладка 'Работники'."""
        tab = self.tabview.tab("Работники")
        EmployeesForm(tab, self.db)

    def _init_work_types_tab(self) -> None:
        """Вкладка 'Виды работ'."""
        tab = self.tabview.tab("Виды работ")
        WorkTypesForm(tab, self.db)

    def _init_reports_tab(self) -> None:
        """Вкладка 'Отчеты'."""
        # ... (предыдущий код из этапа 2)

    def _init_import_export_buttons(self) -> None:
        """Добавление кнопок импорта/экспорта."""
        self._add_buttons_to_tab("Работники")
        self._add_buttons_to_tab("Виды работ")

    def _add_buttons_to_tab(self, tab_name: str) -> None:
        """Добавляет кнопки в указанную вкладку."""
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

    def _export_data(self, table_name: str) -> None:
        """Экспорт данных в Excel."""
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

    def _import_data(self, table_name: str) -> None:
        """Импорт данных из Excel."""
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

    def _reload_current_tab(self) -> None:
        """Перезагружает текущую вкладку."""
        current_tab = self.tabview.get()
        if current_tab == "Работники":
            self._init_employees_tab()
        elif current_tab == "Виды работ":
            self._init_work_types_tab()


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()