# gui/work_types_form.py
from typing import Optional
import customtkinter as ctk
from db.database import Database
from gui.base_form import BaseForm
from gui.dialogs import show_error
from utils.validators import validate_unique_work_type_name


class WorkTypesForm(BaseForm):
    """Форма для управления видами работ с поддержкой ID."""

    def __init__(self, parent: ctk.CTkFrame, db: Database):
        # Добавляем ID в отображаемые колонки
        columns = ["ID", "Наименование", "Единица измерения", "Цена (руб)"]
        super().__init__(parent, db, columns)
        self._load_data()  # Упрощенная загрузка

    def _load_data(self) -> None:
        """Загрузка данных с ID."""
        query = "SELECT id, name, unit, price FROM work_types"
        super()._load_data(query)

    def _add_item(self) -> None:
        """Добавление нового вида работ."""
        dialog = WorkTypeDialog(self, self.db)
        if dialog.result:
            self._load_data()

    def _edit_item(self) -> None:
        """Редактирование с использованием ID."""
        selected = self.table.selection()
        if not selected:
            show_error("Выберите вид работ!")
            return
        item_data = self.table.item(selected[0])["values"]
        # Передаем ID для обновления
        dialog = WorkTypeDialog(self, self.db, item_data)
        if dialog.result:
            self._load_data()

    def _delete_item(self) -> None:
        """Удаление по ID с проверкой связей."""
        selected = self.table.selection()
        if not selected:
            show_error("Выберите вид работ!")
            return
        work_id = self.table.item(selected[0])["values"][0]

        # Проверка использования в нарядах
        usage = self.db.execute_query(
            "SELECT COUNT(*) FROM order_work_types WHERE work_type_id = ?", (work_id,)
        )
        if usage and usage[0][0] > 0:
            show_error("Невозможно удалить: вид работ используется в нарядах")
            return

        self.db.execute_query("DELETE FROM work_types WHERE id = ?", (work_id,))
        self._load_data()


class WorkTypeDialog(ctk.CTkToplevel):
    """Диалог с поддержкой ID для обновления данных."""

    def __init__(self, parent: ctk.CTkFrame, db: Database, data: Optional[list] = None):
        super().__init__(parent)
        self.db = db
        self.result = False
        self.title("Редактирование" if data else "Добавление")
        self.geometry("400x250")

        # Скрытое поле для ID
        self.work_id = None
        if data:
            self.work_id = data[0]  # ID из первой колонки

        # Основные поля
        self.name_entry = ctk.CTkEntry(self, placeholder_text="Наименование*")
        self.unit_combobox = ctk.CTkComboBox(self, values=["штуки", "комплекты"])
        self.price_entry = ctk.CTkEntry(self, placeholder_text="Цена*")

        # Заполнение данных при редактировании
        if data:
            self.name_entry.insert(0, data[1])
            self.unit_combobox.set(data[2])
            self.price_entry.insert(0, str(data[3]))

        # Размещение элементов
        self.name_entry.pack(pady=5)
        self.unit_combobox.pack(pady=5)
        self.price_entry.pack(pady=5)

        # Кнопки
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame,
            text="Сохранить",
            command=self._save
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Отмена",
            command=self.destroy
        ).pack(side="right", padx=5)

    def _save(self) -> None:
        """Сохранение с использованием ID для обновления."""
        name = self.name_entry.get().strip()
        unit = self.unit_combobox.get()
        price = self.price_entry.get().strip()

        if not all([name, unit, price]):
            show_error("Заполните все обязательные поля!")
            return

        if not validate_unique_work_type_name(name, self.db, exclude_id=self.work_id):
            show_error("Такое наименование уже существует!")
            return

        try:
            price = float(price)
            if price <= 0:
                raise ValueError
        except ValueError:
            show_error("Цена должна быть положительным числом!")
            return

        # Обновление или вставка
        if self.work_id:
            query = """
                UPDATE work_types 
                SET name = ?, unit = ?, price = ?
                WHERE id = ?
            """
            params = (name, unit, price, self.work_id)
        else:
            query = """
                INSERT INTO work_types (name, unit, price)
                VALUES (?, ?, ?)
            """
            params = (name, unit, price)

        self.db.execute_query(query, params)
        self.result = True
        self.destroy()