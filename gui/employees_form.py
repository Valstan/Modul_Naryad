# gui/employees_form.py
from typing import Optional

import customtkinter as ctk
from db.database import Database
from gui.base_form import BaseForm
from gui.dialogs import show_error, show_info
from utils.validators import validate_unique_employee_id


class EmployeesForm(BaseForm):
    """Форма для управления данными работников."""

    def __init__(self, parent: ctk.CTkFrame, db: Database):
        columns = ["Табельный №", "ФИО", "Цех", "Должность"]
        super().__init__(parent, db, columns)
        self._load_data("SELECT employee_id, full_name, workshop_number, position FROM employees")

    def _add_item(self) -> None:
        """Открытие диалога добавления работника."""
        dialog = EmployeeDialog(self, self.db)
        if dialog.result:
            self._load_data("SELECT employee_id, full_name, workshop_number, position FROM employees")

    def _edit_item(self) -> None:
        """Открытие диалога редактирования работника."""
        selected = self.table.selection()
        if not selected:
            show_error("Выберите работника!")
            return

        employee_data = self.table.item(selected[0])["values"]
        dialog = EmployeeDialog(self, self.db, employee_data)
        if dialog.result:
            self._load_data("SELECT employee_id, full_name, workshop_number, position FROM employees")

    def _delete_item(self) -> None:
        """Удаление выбранного работника."""
        selected = self.table.selection()
        if not selected:
            show_error("Выберите работника!")
            return

        employee_id = self.table.item(selected[0])["values"][0]
        self.db.execute_query("DELETE FROM employees WHERE employee_id = ?", (employee_id,))
        self._load_data("SELECT employee_id, full_name, workshop_number, position FROM employees")


class EmployeeDialog(ctk.CTkToplevel):
    """Диалог для добавления/редактирования работника."""

    def __init__(self, parent: ctk.CTkFrame, db: Database, data: Optional[list] = None):
        super().__init__(parent)
        self.db = db
        self.result = False
        self.title("Данные работника" if not data else "Редактирование работника")
        self.geometry("400x300")

        # Поля ввода
        self.employee_id = ctk.CTkEntry(self, placeholder_text="Табельный №")
        self.full_name = ctk.CTkEntry(self, placeholder_text="ФИО")
        self.workshop = ctk.CTkEntry(self, placeholder_text="Цех")
        self.position = ctk.CTkEntry(self, placeholder_text="Должность")

        # Заполнение данных, если это редактирование
        if data:
            self.employee_id.insert(0, str(data[1]))  # data[1] = employee_id в таблице
            self.full_name.insert(0, data[2])
            self.workshop.insert(0, str(data[3]))
            self.position.insert(0, data[4])

        # Размещение элементов
        self.employee_id.pack(pady=5)
        self.full_name.pack(pady=5)
        self.workshop.pack(pady=5)
        self.position.pack(pady=5)

        # Кнопки
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="Сохранить", command=self._save).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Отмена", command=self.destroy).pack(side="right", padx=5)

    def _save(self) -> None:
        """Сохранение данных работника."""
        employee_id = self.employee_id.get().strip()
        full_name = self.full_name.get().strip()
        workshop = self.workshop.get().strip()
        position = self.position.get().strip()

        # Валидация
        if not all([employee_id, full_name, workshop, position]):
            show_error("Все поля обязательны для заполнения!")
            return

        if not validate_unique_employee_id(employee_id, self.db):
            show_error("Табельный номер должен быть уникальным!")
            return

        # Сохранение в БД
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