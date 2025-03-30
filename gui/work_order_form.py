# gui/work_order_form.py
from datetime import datetime
from tkinter import ttk
from typing import List, Dict

import customtkinter as ctk

from db.database import Database
from gui.dialogs import DatePickerDialog, WorkerSelectionDialog, show_error
from utils.validators import validate_order_data


class WorkOrderForm(ctk.CTkFrame):
    """Форма для создания и редактирования нарядов работ."""

    def __init__(self, parent: ctk.CTkFrame, db: Database) -> None:
        super().__init__(parent)
        self.db = db
        self._current_workers: List[int] = []
        self._current_works: List[Dict] = []
        self._setup_ui()
        self._load_initial_data()

    def _setup_ui(self) -> None:
        """Инициализация элементов интерфейса."""
        self.pack(expand=True, fill="both", padx=20, pady=20)

        # Поля ввода
        self.order_id_label = ctk.CTkLabel(self, text="Наряд №:")
        self.order_id_label.grid(row=0, column=0, sticky="w")
        self.order_id_value = ctk.CTkLabel(self, text="Автоматически")
        self.order_id_value.grid(row=0, column=1, sticky="w")

        # Дата наряда
        self.date_label = ctk.CTkLabel(self, text="Дата:")
        self.date_label.grid(row=1, column=0, sticky="w")
        self.date_entry = ctk.CTkEntry(self)
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        self.date_entry.grid(row=1, column=1, sticky="ew")
        self.date_picker_btn = ctk.CTkButton(self, text="📅", width=30, command=self._open_date_picker)
        self.date_picker_btn.grid(row=1, column=2, padx=5)

        # Выбор рабочих
        self.workers_btn = ctk.CTkButton(self, text="Выбрать рабочих", command=self._select_workers)
        self.workers_btn.grid(row=2, column=0, columnspan=3, pady=10, sticky="ew")

        # Таблица видов работ
        self.works_table = ttk.Treeview(self, columns=("work_type", "quantity", "amount"), show="headings")
        self.works_table.heading("work_type", text="Вид работы")
        self.works_table.heading("quantity", text="Количество")
        self.works_table.heading("amount", text="Сумма")
        self.works_table.grid(row=3, column=0, columnspan=3, sticky="nsew")

        # Кнопки добавления/удаления работ
        self.add_work_btn = ctk.CTkButton(self, text="+ Добавить работу", command=self._add_work)
        self.add_work_btn.grid(row=4, column=0, pady=10)
        self.remove_work_btn = ctk.CTkButton(self, text="- Удалить работу", command=self._remove_work)
        self.remove_work_btn.grid(row=4, column=1, pady=10)

        # Итоговая сумма
        self.total_label = ctk.CTkLabel(self, text="Итого:")
        self.total_label.grid(row=5, column=0, sticky="w")
        self.total_value = ctk.CTkLabel(self, text="0.00 ₽")
        self.total_value.grid(row=5, column=1, sticky="w")

        # Кнопка сохранения
        self.save_btn = ctk.CTkButton(self, text="Сохранить наряд", command=self._save_order)
        self.save_btn.grid(row=6, column=0, columnspan=3, pady=20, sticky="ew")

    def _load_initial_data(self) -> None:
        """Загрузка данных для выпадающих списков."""
        self.products = self.db.execute_query("SELECT id, name FROM products")
        self.contracts = self.db.execute_query("SELECT id, contract_code FROM contracts")

    def _open_date_picker(self) -> None:
        """Открытие диалога выбора даты."""
        dialog = DatePickerDialog(self)
        date = dialog.get_date()
        if date:
            self.date_entry.delete(0, "end")
            self.date_entry.insert(0, date.strftime("%d.%m.%Y"))

    def _select_workers(self) -> None:
        """Выбор рабочих из списка."""
        dialog = WorkerSelectionDialog(self, self.db)
        workers = dialog.get_selected_workers()
        if workers:
            self._current_workers = workers
            self.workers_btn.configure(text=f"Выбрано: {len(workers)} рабочих")

    def _add_work(self) -> None:
        """Добавление вида работы в таблицу."""
        # Заглушка: здесь будет диалог выбора работы
        work_type = ("Монтаж проводки", 150.0)  # Пример данных
        self._current_works.append({"type_id": 1, "quantity": 5, "price": work_type[1]})
        self._update_works_table()

    def _update_works_table(self) -> None:
        """Обновление таблицы работ."""
        for row in self.works_table.get_children():
            self.works_table.delete(row)

        total = 0.0
        for work in self._current_works:
            amount = work["quantity"] * work["price"]
            self.works_table.insert("", "end", values=(work["type_id"], work["quantity"], f"{amount:.2f} ₽"))
            total += amount

        self.total_value.configure(text=f"{total:.2f} ₽")

    def _save_order(self) -> None:
        is_valid, error_msg = validate_order_data(
            self.date_entry.get(),
            self._current_workers,
            self._current_works,
            self.db
        )

        if not is_valid:
            show_error(error_msg)
            return

# Пример использования диалоговых окон и валидации