# gui/employees_form.py
import customtkinter as ctk
from tkinter import ttk
from db.database import Database
from gui.dialogs import show_error, show_info
from utils.validators import validate_unique_employee_id
from typing import Optional, List


class EmployeesForm(ctk.CTkFrame):
    """Форма для управления данными работников."""

    def __init__(self, parent: ctk.CTkFrame, db: Database) -> None:
        super().__init__(parent)
        self.db = db
        self._setup_ui()
        self._load_employees()

    def _setup_ui(self) -> None:
        """Инициализация элементов интерфейса."""
        self.pack(expand=True, fill="both", padx=20, pady=20)

        # Таблица работников
        self.tree = ttk.Treeview(
            self,
            columns=("employee_id", "full_name", "workshop", "position"),
            show="headings"
        )
        self.tree.heading("employee_id", text="Табельный №")
        self.tree.heading("full_name", text="ФИО")
        self.tree.heading("workshop", text="Цех")
        self.tree.heading("position", text="Должность")
        self.tree.pack(expand=True, fill="both")

        # Кнопки управления
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="Добавить", command=self._open_add_dialog).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Редактировать", command=self._open_edit_dialog).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Удалить", command=self._delete_employee).pack(side="left", padx=5)

    def _load_employees(self) -> None:
        """Загрузка данных работников из БД."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        employees = self.db.execute_query("SELECT * FROM employees")
        for emp in employees:
            self.tree.insert("", "end", values=emp)

    def _open_add_dialog(self) -> None:
        """Открытие диалога добавления работника."""
        dialog = EmployeeDialog(self, self.db)
        if dialog.result:
            self._load_employees()

    def _open_edit_dialog(self) -> None:
        """Открытие диалога редактирования работника."""
        selected = self.tree.selection()
        if not selected:
            show_error("Выберите работника для редактирования!")
            return

        # Получение данных из таблицы с проверкой типа
        item_data = self.tree.item(selected[0])
        values = item_data.get("values", [])

        # Явное приведение к типу List[str] или None
        employee_data: Optional[List[str]] = values if isinstance(values, list) else None

        if not employee_data:
            show_error("Данные работника не найдены или некорректны")
            return

        dialog = EmployeeDialog(self, self.db, employee_data)
        if dialog.result:
            self._load_employees()

    def _delete_employee(self) -> None:
        """Удаление выбранного работника."""
        selected = self.tree.selection()
        if not selected:
            show_error("Выберите работника для удаления!")
            return

        employee_id = self.tree.item(selected[0])["values"][0]
        self.db.execute_query("DELETE FROM employees WHERE id = ?", (employee_id,))
        self._load_employees()


class EmployeeDialog(ctk.CTkToplevel):
    """Диалоговое окно для добавления/редактирования работника."""

    def __init__(self, parent: ctk.CTkFrame, db: Database, data: Optional[List] = None):
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