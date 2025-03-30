# db/backup.py
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional


class BackupManager:
    """Управление резервными копиями БД с проверкой существования файла."""

    def __init__(self, db_path: str, backup_dir: str = "backups", max_backups: int = 20):
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups

        if not self.db_path.exists():
            raise FileNotFoundError(f"Файл БД {db_path} не найден!")

        self._ensure_backup_dir()

    def _ensure_backup_dir(self) -> None:
        """Создать директорию для резервных копий."""
        self.backup_dir.mkdir(exist_ok=True, parents=True)

    def create_backup(self) -> Optional[str]:
        """Создание резервной копии с обработкой ошибок."""
        try:
            # Генерация имени файла
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"backup_{timestamp}.db"

            # Копирование файла
            shutil.copy2(str(self.db_path), str(backup_path))
            self._cleanup_old_backups()
            return str(backup_path)

        except Exception as e:
            print(f"Ошибка резервного копирования: {str(e)}")
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