# gui/work_order_form.py
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple

import customtkinter as ctk
from tkinter import ttk

from db.database import Database
from gui.dialogs import DatePickerDialog, WorkerSelectionDialog, show_error, show_info
from utils.validators import validate_date, validate_positive_number

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
        """Инициализация элементов интерфейса с улучшенной компоновкой."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Заголовок формы
        ctk.CTkLabel(self, text="Новый наряд работ", font=("Arial", 14, "bold")).grid(
            row=0, column=0, columnspan=3, pady=10, sticky="w"
        )

        # Поля ввода
        self._create_input_fields()
        self._create_workers_section()
        self._create_works_table()
        self._create_total_section()
        self._create_control_buttons()

    def _create_input_fields(self) -> None:
        """Создание полей для основных данных наряда."""
        # Дата наряда
        ctk.CTkLabel(self, text="Дата:").grid(row=1, column=0, sticky="e", padx=5)
        self.date_entry = ctk.CTkEntry(self)
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        self.date_entry.grid(row=1, column=1, sticky="ew", padx=5)

        ctk.CTkButton(
            self,
            text="📅",
            width=30,
            command=self._open_date_picker
        ).grid(row=1, column=2, padx=5)

        # Выбор изделия и контракта
        self._create_combobox("Изделие:", "products", row=2)
        self._create_combobox("Контракт:", "contracts", row=3)

    def _create_combobox(self, label: str, table: str, row: int) -> None:
        """Создание выпадающего списка для связанных сущностей."""
        ctk.CTkLabel(self, text=label).grid(row=row, column=0, sticky="e", padx=5)
        values = self._get_combobox_values(table)
        combobox = ctk.CTkComboBox(self, values=values)
        combobox.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
        setattr(self, f"{table}_combobox", combobox)

    def _get_combobox_values(self, table: str) -> List[str]:
        """Загрузка данных для выпадающих списков."""
        try:
            if table == "products":
                result = self.db.execute_query("SELECT id, name FROM products")
            elif table == "contracts":
                result = self.db.execute_query("SELECT id, contract_code FROM contracts")
            return [f"{row[0]} - {row[1]}" for row in result] if result else []
        except Exception as e:
            logger.error(f"Ошибка загрузки {table}: {str(e)}")
            return []

    def _load_initial_data(self) -> None:
        """Инициализация данных для выпадающих списков."""
        try:
            products = self.db.execute_query("SELECT id, name FROM products")
            contracts = self.db.execute_query("SELECT id, contract_code FROM contracts")

            self.products_combobox.configure(
                values=[f"{p[0]} - {p[1]}" for p in products] if products else []
            )
            self.contracts_combobox.configure(
                values=[f"{c[0]} - {c[1]}" for c in contracts] if contracts else []
            )
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {str(e)}")
            show_error("Ошибка загрузки справочников")

    def _create_workers_section(self) -> None:
        """Секция выбора рабочих бригады."""
        self.workers_btn = ctk.CTkButton(
            self,
            text="Выбрать рабочих (0)",
            command=self._select_workers
        )
        self.workers_btn.grid(row=4, column=0, columnspan=3, pady=10, sticky="ew")

    def _create_works_table(self) -> None:
        """Таблица видов работ с улучшенным стилем."""
        columns = ("Вид работы", "Количество", "Цена", "Сумма")
        self.works_table = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
            height=6
        )

        for col in columns:
            self.works_table.heading(col, text=col)
            self.works_table.column(col, width=120, anchor="center")

        self.works_table.grid(row=5, column=0, columnspan=3, sticky="nsew", pady=10)

    def _create_total_section(self) -> None:
        """Секция отображения итоговой суммы."""
        ctk.CTkLabel(self, text="Итого:").grid(row=6, column=0, sticky="e", padx=5)
        self.total_value = ctk.CTkLabel(self, text="0.00 ₽")
        self.total_value.grid(row=6, column=1, sticky="w", padx=5)

    def _create_control_buttons(self) -> None:
        """Кнопки управления нарядом."""
        btn_frame = ctk.CTkFrame(self)
        btn_frame.grid(row=7, column=0, columnspan=3, pady=10)

        ctk.CTkButton(
            btn_frame,
            text="Добавить работу",
            command=self._add_work
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Удалить работу",
            command=self._remove_work
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Сохранить наряд",
            command=self._save_order
        ).pack(side="right", padx=5)

    def _open_date_picker(self) -> None:
        """Обработчик выбора даты с валидацией."""
        dialog = DatePickerDialog(self)
        date = dialog.get_date()
        if date:
            self.date_entry.delete(0, "end")
            self.date_entry.insert(0, date.strftime("%d.%m.%Y"))

    def _select_workers(self) -> None:
        """Выбор рабочих с обновлением счетчика."""
        dialog = WorkerSelectionDialog(self, self.db)
        workers = dialog.get_selected_workers()
        if workers:
            self._current_workers = workers
            self.workers_btn.configure(text=f"Выбрано: {len(workers)} рабочих")

    def _add_work(self) -> None:
        """Добавление вида работы через диалоговое окно."""
        try:
            work_types = self.db.execute_query(
                "SELECT id, name, price FROM work_types"
            )
            if not work_types:
                show_error("Нет доступных видов работ")
                return

            dialog = WorkTypeSelectionDialog(self, work_types)
            selected = dialog.get_selected_work()
            if selected:
                self._current_works.append({
                    "type_id": selected[0],
                    "name": selected[1],
                    "price": selected[2],
                    "quantity": selected[3]
                })
                self._update_works_table()
        except Exception as e:
            logger.error(f"Ошибка добавления работы: {str(e)}")
            show_error("Ошибка при выборе вида работ")

    def _update_works_table(self) -> None:
        """Обновление таблицы с пересчетом сумм."""
        for row in self.works_table.get_children():
            self.works_table.delete(row)

        total = 0.0
        for work in self._current_works:
            amount = work["price"] * work["quantity"]
            self.works_table.insert("", "end", values=(
                work["name"],
                work["quantity"],
                f"{work['price']:.2f} ₽",
                f"{amount:.2f} ₽"
            ))
            total += amount

        self.total_value.configure(text=f"{total:.2f} ₽")

    def _remove_work(self) -> None:
        """Удаление выбранной работы из таблицы."""
        selected = self.works_table.selection()
        if not selected:
            show_error("Выберите работу для удаления")
            return

        index = self.works_table.index(selected[0])
        del self._current_works[index]
        self._update_works_table()

    def _save_order(self) -> None:
        """Сохранение наряда с полной валидацией."""
        try:
            # Валидация основных полей
            errors = self._validate_basic_fields()
            if errors:
                show_error("\n".join(errors))
                return

            # Валидация связанных данных
            product_id = self._get_selected_id("products")
            contract_id = self._get_selected_id("contracts")
            if not product_id or not contract_id:
                show_error("Не выбрано изделие или контракт")
                return

            # Сохранение в БД
            order_id = self._save_to_database(product_id, contract_id)
            self._save_related_data(order_id)

            show_info("Наряд успешно сохранен")
            self._clear_form()
        except Exception as e:
            logger.error(f"Ошибка сохранения наряда: {str(e)}")
            show_error("Ошибка сохранения данных")

    def _validate_basic_fields(self) -> List[str]:
        """Валидация обязательных полей формы."""
        errors = []
        if not validate_date(self.date_entry.get()):
            errors.append("Неверный формат даты (дд.мм.гггг)")
        if not self._current_workers:
            errors.append("Выберите минимум одного рабочего")
        if not self._current_works:
            errors.append("Добавьте минимум один вид работ")
        return errors

    def _get_selected_id(self, field: str) -> Optional[int]:
        """Получение ID выбранного элемента из комбобокса."""
        value = getattr(self, f"{field}_combobox").get()
        return int(value.split(" - ")[0]) if value else None

    def _save_to_database(self, product_id: int, contract_id: int) -> int:
        """Сохранение основного наряда в БД."""
        total = sum(work["price"] * work["quantity"] for work in self._current_works)

        result = self.db.execute_query(
            """INSERT INTO work_orders 
               (order_date, product_id, contract_id, total_amount)
               VALUES (?, ?, ?, ?)
               RETURNING id""",
            (self.date_entry.get(), product_id, contract_id, total)
        )

        if not result:
            raise ValueError("Ошибка сохранения наряда")
        return result[0][0]

    def _save_related_data(self, order_id: int) -> None:
        """Сохранение связанных данных (работники и виды работ)."""
        # Сохранение рабочих
        workers_data = [(order_id, worker_id) for worker_id in self._current_workers]
        self.db.execute_query(
            "INSERT INTO order_workers (order_id, worker_id) VALUES (?, ?)",
            workers_data,
            many=True
        )

        # Сохранение видов работ
        works_data = [
            (order_id, work["type_id"], work["quantity"], work["price"] * work["quantity"])
            for work in self._current_works
        ]
        self.db.execute_query(
            """INSERT INTO order_work_types 
               (order_id, work_type_id, quantity, amount)
               VALUES (?, ?, ?, ?)""",
            works_data,
            many=True
        )

    def _clear_form(self) -> None:
        """Очистка формы после успешного сохранения."""
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        self.products_combobox.set("")
        self.contracts_combobox.set("")
        self._current_workers = []
        self._current_works = []
        self.workers_btn.configure(text="Выбрать рабочих (0)")
        self._update_works_table()


class WorkTypeSelectionDialog(ctk.CTkToplevel):
    """Диалог выбора вида работ с возможностью указания количества."""

    def __init__(self, parent: ctk.CTkFrame, work_types: List[Tuple]):
        super().__init__(parent)
        self.title("Выбор вида работ")
        self.geometry("400x300")
        self._selected = None

        # Таблица видов работ
        self.tree = ttk.Treeview(
            self,
            columns=("Наименование", "Цена"),
            show="headings"
        )
        self.tree.heading("Наименование", text="Наименование")
        self.tree.heading("Цена", text="Цена за ед.")
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

        for wt in work_types:
            self.tree.insert("", "end", values=(wt[1], f"{wt[2]:.2f} ₽"), tags=(wt[0],))

        # Поле для количества
        self.quantity_entry = ctk.CTkEntry(self, placeholder_text="Количество")
        self.quantity_entry.pack(pady=5)

        # Кнопки
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)

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
        """Обработка выбора вида работ."""
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

        self._selected = (
            int(self.tree.item(selected[0], "tags")[0]),  # ID
            self.tree.item(selected[0], "values")[0],  # Наименование
            float(self.tree.item(selected[0], "values")[1].split()[0]),  # Цена
            quantity
        )
        self.destroy()

    def get_selected_work(self) -> Optional[Tuple]:
        return self._selected