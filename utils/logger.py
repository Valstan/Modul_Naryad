# utils/logger.py
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler


def configure_logging() -> None:
    """Конфигурация расширенной системы логирования для всего приложения."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Форматтер с дополнительной информацией
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )

    # Обработчик для файла с ротацией
    file_handler = RotatingFileHandler(
        filename=log_dir / "app.log",
        maxBytes=5*1024*1024,  # 5 MB
        backupCount=10,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    # Консольный обработчик только для ошибок
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)

    # Базовая конфигурация
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler],
    )

    # Отключаем логирование от сторонних библиотек
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.captureWarnings(True)