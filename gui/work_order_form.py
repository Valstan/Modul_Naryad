# gui/work_order_form.py
import logging
from datetime import datetime
from tkinter import ttk
from typing import List, Dict, Optional, Tuple

import customtkinter as ctk

from db.database import Database
from gui.dialogs import DatePickerDialog, WorkerSelectionDialog, show_error, show_info
from utils.validators import validate_date

logger = logging.getLogger(__name__)


class WorkOrderForm(ctk.CTkFrame):
    """Форма для создания и редактирования нарядов работ с полной валидацией."""

    def __init__(self, parent: ctk.CTkFrame, db: Database) -> None:
        super().__init__(parent)
        self.db = db
        self._current_workers: List[int] = []
        self._current_works: List[Dict] = []
        self._setup_ui()
        self._load_initial_data()

    def _setup_ui(self) -> None:
        """Полная переработка интерфейса с улучшенной компоновкой."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(5, weight=1)

        # Заголовок формы
        header = ctk.CTkLabel(self, text="Новый наряд работ", font=("Arial", 14, "bold"))
        header.grid(row=0, column=0, columnspan=3, pady=(10, 20), sticky="ew")

        # Основные поля
        self._create_input_fields()
        self._create_workers_section()
        self._create_works_table()
        self._create_total_section()
        self._create_control_buttons()

    def _create_input_fields(self) -> None:
        """Переработанные поля ввода с валидацией."""
        # Дата наряда
        date_frame = ctk.CTkFrame(self)
        date_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        date_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(date_frame, text="Дата:").pack(side="left", padx=(0, 5))
        self.date_entry = ctk.CTkEntry(date_frame)
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        self.date_entry.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            date_frame,
            text="📅",
            width=30,
            command=self._open_date_picker
        ).pack(side="right", padx=(5, 0))

        # Выбор изделия и контракта
        self._create_combobox("Изделие:", "products", row=2)
        self._create_combobox("Контракт:", "contracts", row=3)

    def _create_combobox(self, label: str, table: str, row: int) -> None:
        """Улучшенные выпадающие списки с обновлением."""
        frame = ctk.CTkFrame(self)
        frame.grid(row=row, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame, text=f"{label}").pack(side="left", padx=(0, 5))
        combobox = ctk.CTkComboBox(frame, values=[])
        combobox.pack(side="left", fill="x", expand=True, padx=(0, 5))
        setattr(self, f"{table}_combobox", combobox)

        # Кнопка обновления
        ctk.CTkButton(
            frame,
            text="🔄",
            width=30,
            command=lambda: self._refresh_combobox(table)
        ).pack(side="right")

    def _refresh_combobox(self, table: str) -> None:
        """Обновление данных выпадающего списка."""
        try:
            if table == "products":
                data = self.db.execute_query("SELECT id, name FROM products")
            elif table == "contracts":
                data = self.db.execute_query("SELECT id, contract_code FROM contracts")
            values = [f"{row[0]} - {row[1]}" for row in data] if data else []
            getattr(self, f"{table}_combobox").configure(values=values)
        except Exception as e:
            logger.error(f"Ошибка обновления {table}: {str(e)}")
            show_error(f"Не удалось обновить список {table}")

    def _create_workers_section(self) -> None:
        """Улучшенный выбор рабочих с подсказкой."""
        self.worker_frame = ctk.CTkFrame(self)
        self.worker_frame.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        self.workers_btn = ctk.CTkButton(
            self.worker_frame,
            text="Выбрать рабочих (0)",
            command=self._select_workers
        )
        self.workers_btn.pack(side="left", padx=5, pady=5, fill="x", expand=True)

        ctk.CTkLabel(
            self.worker_frame,
            text="* Минимум 1 рабочий",
            text_color="gray"
        ).pack(side="right", padx=5)

    def _create_works_table(self) -> None:
        """Переработанная таблица работ с полосой прокрутки."""
        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        columns = ("Вид работы", "Количество", "Цена за ед.", "Сумма")
        self.works_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Custom.Treeview"
        )

        for col in columns:
            self.works_table.heading(col, text=col)
            self.works_table.column(col, width=120, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.works_table.yview)
        self.works_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.works_table.grid(row=0, column=0, sticky="nsew")

    def _create_total_section(self) -> None:
        """Отображение итоговой суммы с валютой."""
        total_frame = ctk.CTkFrame(self)
        total_frame.grid(row=6, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        total_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(total_frame, text="Итого:").pack(side="left", padx=(10, 5))
        self.total_value = ctk.CTkLabel(total_frame, text="0.00 ₽", font=("Arial", 12, "bold"))
        self.total_value.pack(side="left")

    def _create_control_buttons(self) -> None:
        """Группа кнопок управления с разделителями."""
        btn_frame = ctk.CTkFrame(self)
        btn_frame.grid(row=7, column=0, columnspan=3, padx=5, pady=(10, 5), sticky="ew")
        btn_frame.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkButton(
            btn_frame,
            text="Добавить работу",
            command=self._add_work
        ).grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        ctk.CTkButton(
            btn_frame,
            text="Удалить работу",
            command=self._remove_work
        ).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkButton(
            btn_frame,
            text="Сохранить наряд",
            command=self._save_order
        ).grid(row=0, column=2, padx=5, pady=5, sticky="ew")

    def _load_initial_data(self) -> None:
        """Загрузка начальных данных с обработкой ошибок."""
        try:
            self._refresh_combobox("products")
            self._refresh_combobox("contracts")
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {str(e)}")
            show_error("Ошибка загрузки справочников")

    def _open_date_picker(self) -> None:
        """Улучшенный выбор даты с валидацией."""
        dialog = DatePickerDialog(self)
        self.wait_window(dialog)
        selected_date = dialog.get_date()
        if selected_date:
            formatted_date = selected_date.strftime("%d.%m.%Y")
            if validate_date(formatted_date):
                self.date_entry.delete(0, "end")
                self.date_entry.insert(0, formatted_date)
            else:
                show_error("Неверный формат даты")

    def _select_workers(self) -> None:
        """Выбор рабочих с обновлением интерфейса."""
        dialog = WorkerSelectionDialog(self, self.db)
        self.wait_window(dialog)
        workers = dialog.get_selected_workers()
        if workers:
            self._current_workers = workers
            self.workers_btn.configure(text=f"Выбрано: {len(workers)} рабочих")

    def _add_work(self) -> None:
        """Добавление работы с выбором из существующих."""
        try:
            work_types = self.db.execute_query(
                "SELECT id, name, price, unit FROM work_types"
            )
            if not work_types:
                show_error("Нет доступных видов работ")
                return

            dialog = WorkTypeSelectionDialog(self, work_types)
            self.wait_window(dialog)
            selected = dialog.get_selected_work()

            if selected:
                self._current_works.append({
                    "type_id": selected[0],
                    "name": selected[1],
                    "price": selected[2],
                    "quantity": selected[3],
                    "unit": selected[4]
                })
                self._update_works_table()

        except Exception as e:
            logger.error(f"Ошибка добавления работы: {str(e)}")
            show_error("Ошибка при добавлении работы")

    def _update_works_table(self) -> None:
        """Обновление таблицы работ с пересчетом сумм."""
        try:
            self.works_table.delete(*self.works_table.get_children())
            total = 0.0

            for work in self._current_works:
                amount = work["price"] * work["quantity"]
                total += amount
                self.works_table.insert("", "end", values=(
                    work["name"],
                    f"{work['quantity']} {work['unit']}",
                    f"{work['price']:.2f} ₽",
                    f"{amount:.2f} ₽"
                ))

            self.total_value.configure(text=f"{total:.2f} ₽")

        except Exception as e:
            logger.error(f"Ошибка обновления таблицы: {str(e)}")
            show_error("Ошибка отображения работ")

    def _remove_work(self) -> None:
        """Удаление работы с подтверждением."""
        selected = self.works_table.selection()
        if not selected:
            show_error("Выберите работу для удаления")
            return

        confirm = show_info("Удалить выбранную работу?", need_confirm=True)
        if confirm:
            index = self.works_table.index(selected[0])
            del self._current_works[index]
            self._update_works_table()

    def _save_order(self) -> None:
        """Сохранение наряда с комплексной валидацией."""
        try:
            # Валидация основных полей
            errors = []
            if not validate_date(self.date_entry.get()):
                errors.append("Неверная дата")
            if not self._current_workers:
                errors.append("Не выбраны рабочие")
            if not self._current_works:
                errors.append("Нет работ")

            # Проверка выбора изделия и контракта
            product_id = self._get_selected_id("products")
            contract_id = self._get_selected_id("contracts")
            if not product_id:
                errors.append("Не выбрано изделие")
            if not contract_id:
                errors.append("Не выбран контракт")

            if errors:
                show_error(" ".join(errors))
                return

            # Сохранение в БД
            order_id = self._save_to_database(product_id, contract_id)
            self._save_related_data(order_id)
            show_info("Наряд сохранен")
            self._clear_form()

        except Exception as e:
            logger.error(f"Ошибка сохранения: {str(e)}")
            show_error("Не удалось сохранить наряд")

    def _get_selected_id(self, field: str) -> Optional[int]:
        """Получение ID из выпадающего списка."""
        combobox = getattr(self, f"{field}_combobox")
        value = combobox.get()
        return int(value.split(" - ")[0]) if value else None

    def _save_to_database(self, product_id: int, contract_id: int) -> int:
        """Сохранение основной записи наряда."""
        total = sum(w["price"] * w["quantity"] for w in self._current_works)
        result = self.db.execute_query(
            """INSERT INTO work_orders 
               (order_date, product_id, contract_id, total_amount)
               VALUES (?, ?, ?, ?)
               RETURNING id""",
            (self.date_entry.get(), product_id, contract_id, total)
        )
        return result[0][0] if result else None

    def _save_related_data(self, order_id: int) -> None:
        """Сохранение связанных данных в БД."""
        # Сохранение рабочих
        workers_data = [(order_id, worker_id) for worker_id in self._current_workers]
        self.db.execute_query(
            "INSERT INTO order_workers (order_id, worker_id) VALUES (?, ?)",
            workers_data,
            many=True
        )

        # Сохранение работ
        works_data = [
            (order_id, w["type_id"], w["quantity"], w["price"] * w["quantity"])
            for w in self._current_works
        ]
        self.db.execute_query(
            """INSERT INTO order_work_types 
               (order_id, work_type_id, quantity, amount)
               VALUES (?, ?, ?, ?)""",
            works_data,
            many=True
        )

    def _clear_form(self) -> None:
        """Очистка формы после сохранения."""
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        self.products_combobox.set("")
        self.contracts_combobox.set("")
        self._current_workers = []
        self._current_works = []
        self.workers_btn.configure(text="Выбрать рабочих (0)")
        self._update_works_table()


class WorkTypeSelectionDialog(ctk.CTkToplevel):
    """Диалог выбора вида работ с поддержкой единиц измерения."""

    def __init__(self, parent: ctk.CTkFrame, work_types: List[Tuple]):
        super().__init__(parent)
        self.title("Выбор вида работ")
        self.geometry("500x350")
        self._selected = None

        # Таблица видов работ
        self.tree = ttk.Treeview(
            self,
            columns=("Наименование", "Ед.изм.", "Цена"),
            show="headings"
        )
        self.tree.heading("Наименование", text="Наименование")
        self.tree.heading("Ед.изм.", text="Ед. изм.")
        self.tree.heading("Цена", text="Цена за ед.")
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

        for wt in work_types:
            self.tree.insert("", "end", values=(
                wt[1],
                wt[3],
                f"{wt[2]:.2f} ₽"
            ), tags=(wt[0],))

        # Поля ввода
        self.quantity_frame = ctk.CTkFrame(self)
        self.quantity_frame.pack(padx=10, pady=5, fill="x")

        ctk.CTkLabel(self.quantity_frame, text="Количество:").pack(side="left", padx=5)
        self.quantity_entry = ctk.CTkEntry(self.quantity_frame)
        self.quantity_entry.pack(side="left", fill="x", expand=True)

        # Кнопки
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(padx=10, pady=10)

        ctk.CTkButton(
            btn_frame,
            text="Выбрать",
            command=self._on_select
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Отмена",
            command=self.destroy
        ).pack(side="right", padx=5)

    def _on_select(self) -> None:
        """Обработка выбора работы с валидацией."""
        selected = self.tree.selection()
        if not selected:
            show_error("Выберите вид работ")
            return

        try:
            quantity = int(self.quantity_entry.get())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            show_error("Введите корректное количество")
            return

        item = self.tree.item(selected[0])
        work_id = int(item["tags"][0])
        work_data = (
            work_id,
            item["values"][0],
            float(item["values"][2].split()[0]),
            quantity,
            item["values"][1]
        )
        self._selected = work_data
        self.destroy()

    def get_selected_work(self) -> Optional[Tuple]:
        return self._selected