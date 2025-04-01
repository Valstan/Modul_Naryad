# utils/logger.py
import logging
from pathlib import Path


def configure_logging():
    """Конфигурация системы логирования для всего приложения"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "app.log"),
            logging.StreamHandler()
        ]
    )
    logging.captureWarnings(True)