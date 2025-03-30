# gui/base_form.py
import customtkinter as ctk
from tkinter import ttk
from typing import List, Optional, Tuple
from db.database import Database


class BaseForm(ctk.CTkFrame):
    """Базовый класс для всех форм с таблицей и кнопками управления."""

    def __init__(self, parent: ctk.CTkFrame, db: Database, columns: List[str]):
        super().__init__(parent)
        self.db = db
        self.columns = columns
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Инициализация интерфейса."""
        # Таблица
        self.table = ttk.Treeview(
            self,
            columns=self.columns,
            show="headings",
            style="Custom.Treeview"
        )
        for col in self.columns:
            self.table.heading(col, text=col)
        self.table.pack(expand=True, fill="both", padx=10, pady=10)

        # Кнопки управления
        self.btn_frame = ctk.CTkFrame(self)
        self.btn_frame.pack(pady=10)

        self.add_btn = ctk.CTkButton(self.btn_frame, text="Добавить", command=self._add_item)
        self.add_btn.pack(side="left", padx=5)

        self.edit_btn = ctk.CTkButton(self.btn_frame, text="Редактировать", command=self._edit_item)
        self.edit_btn.pack(side="left", padx=5)

        self.delete_btn = ctk.CTkButton(self.btn_frame, text="Удалить", command=self._delete_item)
        self.delete_btn.pack(side="left", padx=5)

    def _load_data(self, query: str, params: Optional[Tuple] = None) -> None:
        """Загружает данные из БД в таблицу."""
        for row in self.table.get_children():
            self.table.delete(row)
        data = self.db.execute_query(query, params)
        for item in data:
            self.table.insert("", "end", values=item)

    def _add_item(self) -> None:
        """Добавление элемента (реализуется в дочерних классах)."""
        raise NotImplementedError

    def _edit_item(self) -> None:
        """Редактирование элемента (реализуется в дочерних классах)."""
        raise NotImplementedError

    def _delete_item(self) -> None:
        """Удаление элемента (реализуется в дочерних классах)."""
        raise NotImplementedError