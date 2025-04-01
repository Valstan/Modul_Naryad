# main.py
import sys
import logging
from db.backup import BackupManager
from gui.dialogs import show_error
from gui.main_window import MainWindow
from utils.logger import configure_logging

logger = logging.getLogger(__name__)


def main() -> None:
    """Точка входа в программу."""
    configure_logging()

    try:
        logger.info("Starting application initialization")
        BackupManager("work_orders.db").create_backup()

        logger.debug("Creating main window")
        app = MainWindow()
        app.protocol("WM_DELETE_WINDOW", app.quit)

        logger.info("Starting main loop")
        app.mainloop()

    except Exception as e:
        logger.critical(f"Critical error: {str(e)}", exc_info=True)
        show_error(f"Критическая ошибка: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()