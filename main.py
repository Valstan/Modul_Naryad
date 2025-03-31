# main.py
from db.backup import BackupManager
from gui.dialogs import show_error
from gui.main_window import MainWindow


def main() -> None:
    """Точка входа в программу."""
    try:
        # Создать резервную копию БД при запуске
        BackupManager("work_orders.db").create_backup()

        # Инициализация GUI
        app = MainWindow()
        app.mainloop()

    except Exception as e:
        show_error(f"Критическая ошибка: {str(e)}")


if __name__ == "__main__":
    main()