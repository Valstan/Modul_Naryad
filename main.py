# main.py
import sys
import logging
from db.backup import BackupManager
from db.database import Database
from gui.dialogs import show_error
from gui.main_window import MainWindow
from utils.logger import configure_logging

logger = logging.getLogger(__name__)


def main() -> None:
    """Точка входа в программу."""
    configure_logging()

    try:
        logger.info("Запуск приложения")
        db = Database()
        BackupManager(str(db.db_path)).create_backup()
        app = MainWindow(db)
        app.mainloop()
    except Exception as e:
        logger.critical(f"Критическая ошибка: {str(e)}", exc_info=True)
        show_error(f"Ошибка запуска: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()