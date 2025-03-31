# gui/dialogs.py
from tkinter import ttk

import customtkinter as ctk
from tkcalendar import Calendar
from datetime import datetime
from typing import List, Optional, Tuple
from db.database import Database


class DatePickerDialog(ctk.CTkToplevel):
    """Диалоговое окно выбора даты."""

    def __init__(self, parent: ctk.CTkFrame) -> None:
        super().__init__(parent)
        self.title("Выбор даты")
        self.geometry("300x200")
        self.resizable(False, False)
        self._selected_date: Optional[datetime] = None

        # Календарь из tkcalendar
        self.calendar = Calendar(self, selectmode="day", date_pattern="dd.mm.yyyy")
        self.calendar.pack(pady=10)

        # Кнопки
        self.btn_frame = ctk.CTkFrame(self)
        self.btn_frame.pack(pady=10)

        self.ok_btn = ctk.CTkButton(self.btn_frame, text="OK", command=self._on_ok)
        self.ok_btn.pack(side="left", padx=5)

        self.cancel_btn = ctk.CTkButton(self.btn_frame, text="Отмена", command=self.destroy)
        self.cancel_btn.pack(side="right", padx=5)

    def _on_ok(self) -> None:
        """Обработка выбора даты."""
        try:
            self._selected_date = datetime.strptime(self.calendar.get_date(), "%d.%m.%Y")
            self.destroy()
        except ValueError:
            self._selected_date = None

    def get_date(self) -> Optional[datetime]:
        """Возвращает выбранную дату."""
        return self._selected_date


class WorkerSelectionDialog(ctk.CTkToplevel):
    """Диалоговое окно выбора рабочих."""

    def __init__(self, parent: ctk.CTkFrame, db: Database) -> None:
        super().__init__(parent)
        self.title("Выбор рабочих")
        self.geometry("600x400")
        self.db = db
        self._selected_ids: List[int] = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Инициализация интерфейса."""
        # Таблица работников
        self.tree = ttk.Treeview(self, columns=("id", "name", "workshop"), show="headings")
        self.tree.heading("id", text="Табельный №")
        self.tree.heading("name", text="ФИО")
        self.tree.heading("workshop", text="Цех")
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

        # Загрузка данных
        workers = self.db.execute_query("SELECT employee_id, full_name, workshop_number FROM employees")
        for worker in workers:
            self.tree.insert("", "end", values=worker)

        # Кнопки
        self.btn_frame = ctk.CTkFrame(self)
        self.btn_frame.pack(pady=10)

        self.select_btn = ctk.CTkButton(self.btn_frame, text="Выбрать", command=self._on_select)
        self.select_btn.pack(side="left", padx=5)

        self.cancel_btn = ctk.CTkButton(self.btn_frame, text="Отмена", command=self.destroy)
        self.cancel_btn.pack(side="right", padx=5)

    def _on_select(self) -> None:
        """Обработка выбранных рабочих."""
        selected_items = self.tree.selection()
        self._selected_ids = [int(self.tree.item(item)["values"][0]) for item in selected_items]
        self.destroy()

    def get_selected_workers(self) -> List[int]:
        """Возвращает список ID выбранных рабочих."""
        return self._selected_ids


def show_error(message: str) -> None:
    """Отображает окно с сообщением об ошибке."""
    dialog = ctk.CTkToplevel()
    dialog.title("Ошибка")
    dialog.geometry("400x100")

    label = ctk.CTkLabel(dialog, text=message, text_color="red")
    label.pack(pady=20)

    btn = ctk.CTkButton(dialog, text="OK", command=dialog.destroy)
    btn.pack(pady=5)


def show_info(message: str) -> None:
    """Отображает информационное сообщение."""
    dialog = ctk.CTkToplevel()
    dialog.title("Информация")
    dialog.geometry("400x100")

    label = ctk.CTkLabel(dialog, text=message)
    label.pack(pady=20)

    btn = ctk.CTkButton(dialog, text="OK", command=dialog.destroy)
    btn.pack(pady=5)