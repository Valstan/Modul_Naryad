# gui/work_types_form.py
from typing import Optional

import customtkinter as ctk

from db.database import Database
from gui.base_form import BaseForm
from gui.dialogs import show_error
from utils.validators import validate_unique_work_type_name


class WorkTypesForm(BaseForm):
    """Форма для управления видами работ."""

    def __init__(self, parent: ctk.CTkFrame, db: Database):
        columns = ["Наименование", "Единица измерения", "Цена (руб)"]
        super().__init__(parent, db, columns)
        self._load_data("SELECT name, unit, price FROM work_types")

    def _add_item(self) -> None:
        """Открытие диалога добавления вида работ."""
        dialog = WorkTypeDialog(self, self.db)
        if dialog.result:
            self._load_data("SELECT name, unit, price FROM work_types")

    def _edit_item(self) -> None:
        """Редактирование выбранного вида работ."""
        selected = self.table.selection()
        if not selected:
            show_error("Выберите вид работ!")
            return

        work_data = self.table.item(selected[0])["values"]
        dialog = WorkTypeDialog(self, self.db, work_data)
        if dialog.result:
            self._load_data("SELECT name, unit, price FROM work_types")

    def _delete_item(self) -> None:
        """Удаление выбранного вида работ."""
        selected = self.table.selection()
        if not selected:
            show_error("Выберите вид работ!")
            return

        work_name = self.table.item(selected[0])["values"][0]
        self.db.execute_query("DELETE FROM work_types WHERE name = ?", (work_name,))
        self._load_data("SELECT name, unit, price FROM work_types")


class WorkTypeDialog(ctk.CTkToplevel):
    """Диалог для добавления/редактирования вида работ."""

    def __init__(self, parent: ctk.CTkFrame, db: Database, data: Optional[list] = None):
        super().__init__(parent)
        self.db = db
        self.result = False
        self.title("Новый вид работ" if not data else "Редактирование")
        self.geometry("400x250")

        # Поля ввода
        self.name_entry = ctk.CTkEntry(self, placeholder_text="Наименование*")
        self.unit_combobox = ctk.CTkComboBox(self, values=["штуки", "комплекты"])
        self.price_entry = ctk.CTkEntry(self, placeholder_text="Цена*")

        # Заполнение данных
        if data:
            self.name_entry.insert(0, data[0])
            self.unit_combobox.set(data[1])
            self.price_entry.insert(0, str(data[2]))

        # Размещение элементов
        self.name_entry.pack(pady=5)
        self.unit_combobox.pack(pady=5)
        self.price_entry.pack(pady=5)

        # Кнопки
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="Сохранить", command=self._save).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Отмена", command=self.destroy).pack(side="right", padx=5)

    def _save(self) -> None:
        """Сохранение данных."""
        name = self.name_entry.get().strip()
        unit = self.unit_combobox.get()
        price = self.price_entry.get().strip()

        # Валидация
        if not all([name, unit, price]):
            show_error("Заполните все обязательные поля!")
            return

        if not validate_unique_work_type_name(name, self.db):
            show_error("Наименование должно быть уникальным!")
            return

        try:
            price = float(price)
        except ValueError:
            show_error("Некорректное значение цены!")
            return

        # Сохранение в БД
        query = """
            INSERT INTO work_types (name, unit, price)
            VALUES (?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                unit = excluded.unit,
                price = excluded.price
        """
        self.db.execute_query(query, (name, unit, price))
        self.result = True
        self.destroy()