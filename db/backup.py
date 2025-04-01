# db/backup.py
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class BackupManager:
    """Управление резервными копиями БД с автоматическим созданием директории."""

    def __init__(self, db_path: str, backup_dir: str = "backups", max_backups: int = 20):
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups
        self._ensure_backup_dir()

    def _ensure_backup_dir(self) -> None:
        """Создать директории для резервных копий."""
        self.backup_dir.mkdir(exist_ok=True, parents=True)

    def create_backup(self) -> Optional[str]:
        """Создание резервной копии с обработкой отсутствия файла."""
        try:
            if not self.db_path.exists():
                logger.warning(f"Файл БД {self.db_path} не найден, резервная копия не создана")
                return None

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"backup_{timestamp}.db"
            shutil.copy2(str(self.db_path), str(backup_path))
            self._cleanup_old_backups()
            logger.info(f"Создана резервная копия: {backup_path}")
            return str(backup_path)

        except Exception as e:
            logger.error(f"Ошибка резервного копирования: {str(e)}", exc_info=True)
            return None

    def _cleanup_old_backups(self) -> None:
        """Удаление старых копий, если превышен лимит."""
        backups = sorted(
            self.backup_dir.glob("backup_*.db"),
            key=lambda x: x.stat().st_mtime,
            reverse=False
        )

        while len(backups) > self.max_backups:
            old_backup = backups.pop(0)
            os.remove(str(old_backup))