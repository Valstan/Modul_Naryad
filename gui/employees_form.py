# gui/employees_form.py
from typing import Optional
import customtkinter as ctk
from db.database import Database
from gui.base_form import BaseForm
from gui.dialogs import show_error, show_info
from utils.validators import validate_unique_employee_id


class EmployeesForm(BaseForm):
    """Форма для управления данными работников с исправленной загрузкой данных."""

    def __init__(self, parent: ctk.CTkFrame, db: Database):
        columns = ["Табельный №", "ФИО", "Цех", "Должность"]
        super().__init__(parent, db, columns)
        self._load_data()  # Упрощенная загрузка

    def _load_data(self) -> None:
        """Исправленная загрузка данных с правильным запросом."""
        query = "SELECT employee_id, full_name, workshop_number, position FROM employees"
        super()._load_data(query)

    def _add_item(self) -> None:
        """Открытие диалога добавления работника с обновлением данных."""
        dialog = EmployeeDialog(self, self.db)
        if dialog.result:
            self._load_data()  # Перезагрузка после сохранения

    def _edit_item(self) -> None:
        """Исправленное редактирование с корректной передачей данных."""
        selected = self.table.selection()
        if not selected:
            show_error("Выберите работника!")
            return
        item_data = self.table.item(selected[0])["values"]
        # Формируем данные в правильном порядке
        employee_data = (
            item_data[0],  # Табельный №
            item_data[1],  # ФИО
            item_data[2],  # Цех
            item_data[3]  # Должность
        )
        dialog = EmployeeDialog(self, self.db, employee_data)
        if dialog.result:
            self._load_data()

    def _delete_item(self) -> None:
        """Удаление с проверкой использования в нарядах."""
        selected = self.table.selection()
        if not selected:
            show_error("Выберите работника!")
            return
        employee_id = self.table.item(selected[0])["values"][0]

        # Проверка наличия в нарядах
        orders_count = self.db.execute_query(
            "SELECT COUNT(*) FROM order_workers WHERE worker_id = (SELECT id FROM employees WHERE employee_id = ?)",
            (employee_id,)
        )
        if orders_count and orders_count[0][0] > 0:
            show_error("Невозможно удалить: работник участвует в нарядах")
            return

        self.db.execute_query(
            "DELETE FROM employees WHERE employee_id = ?",
            (employee_id,)
        )
        self._load_data()


class EmployeeDialog(ctk.CTkToplevel):
    """Диалог для добавления/редактирования работника с исправленными индексами."""

    def __init__(self, parent: ctk.CTkFrame, db: Database, data: Optional[tuple] = None):
        super().__init__(parent)
        self.db = db
        self.result = False
        self.title("Редактирование" if data else "Добавление")
        self.geometry("400x300")

        # Исправленные поля ввода
        self.employee_id = ctk.CTkEntry(self, placeholder_text="Табельный №")
        self.full_name = ctk.CTkEntry(self, placeholder_text="ФИО")
        self.workshop = ctk.CTkEntry(self, placeholder_text="Цех")
        self.position = ctk.CTkEntry(self, placeholder_text="Должность")

        # Заполнение данных
        if data:
            self.employee_id.insert(0, data[0])
            self.full_name.insert(0, data[1])
            self.workshop.insert(0, str(data[2]))
            self.position.insert(0, data[3])

        # Размещение элементов
        self.employee_id.pack(pady=5, padx=10, fill="x")
        self.full_name.pack(pady=5, padx=10, fill="x")
        self.workshop.pack(pady=5, padx=10, fill="x")
        self.position.pack(pady=5, padx=10, fill="x")

        # Кнопки
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=20)

        ctk.CTkButton(
            btn_frame,
            text="Сохранить",
            command=self._save
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="Отмена",
            command=self.destroy
        ).pack(side="right", padx=10)

    def _save(self) -> None:
        """Сохранение с проверкой существования работника."""
        employee_id = self.employee_id.get().strip()
        full_name = self.full_name.get().strip()
        workshop = self.workshop.get().strip()
        position = self.position.get().strip()

        if not all([employee_id, full_name, workshop, position]):
            show_error("Все поля обязательны!")
            return

        if not validate_unique_employee_id(employee_id, self.db):
            show_error("Табельный номер должен быть уникальным!")
            return

        # Исправленный SQL-запрос
        query = """
            INSERT INTO employees (employee_id, full_name, workshop_number, position)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(employee_id) DO UPDATE SET
                full_name = excluded.full_name,
                workshop_number = excluded.workshop_number,
                position = excluded.position
        """
        self.db.execute_query(query, (employee_id, full_name, workshop, position))
        self.result = True
        self.destroy()