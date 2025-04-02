# main.py
import sys
import logging
import tkinter as tk
from db.backup import BackupManager
from db.database import Database
from gui.dialogs import show_error
from gui.main_window import MainWindow
from utils.logger import configure_logging

logger = logging.getLogger(__name__)


def main() -> None:
    """Точка входа в программу с улучшенной обработкой ошибок."""
    try:
        configure_logging()
        logger.info("Инициализация приложения")

        # Инициализация базы данных
        db = Database()
        BackupManager(str(db.db_path)).create_backup()

        # Инициализация GUI
        logger.debug("Создание главного окна")
        app = MainWindow(db)

        # Явный запуск главного цикла
        logger.info("Запуск основного цикла приложения")
        app.mainloop()

        logger.info("Приложение завершило работу")

    except Exception as e:
        logger.critical(f"Критическая ошибка инициализации: {str(e)}", exc_info=True)
        show_error(f"Фатальная ошибка: {str(e)}\nПодробности в логах")
        sys.exit(1)

    finally:
        if 'app' in locals():
            try:
                app.destroy()
            except tk.TclError:
                pass


if __name__ == "__main__":
    main()