import pytest
from pathlib import Path
from db.database import Database
from db.backup import BackupManager

TEST_DB_PATH = "test_work_orders.db"


@pytest.fixture(scope="function")
def test_db():
    """Фикстура для создания и удаления тестовой БД перед каждым тестом."""
    db = Database()
    db.db_path = TEST_DB_PATH  # Переопределяем путь для тестов

    # Создаем тестовые таблицы
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            employee_id TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            workshop_number INTEGER NOT NULL,
            position TEXT NOT NULL
        )
    """)
    yield db
    # Удаляем тестовую БД после завершения теста
    Path(TEST_DB_PATH).unlink(missing_ok=True)


def test_create_tables(test_db):
    """Проверка создания таблиц."""
    test_db.execute_query(
        "INSERT INTO employees (employee_id, full_name, workshop_number, position) VALUES (?, ?, ?, ?)",
        ("001", "Иванов Иван", 1, "Инженер")
    )
    result = test_db.execute_query("SELECT * FROM employees")
    assert len(result) == 1, "Данные не добавлены в таблицу."


def test_backup_manager(test_db):
    """Проверка создания резервных копий."""
    # Явная проверка существования БД
    assert Path(TEST_DB_PATH).exists(), "Тестовая БД не создана!"

    manager = BackupManager(TEST_DB_PATH, backup_dir="test_backups", max_backups=2)
    backup_path = manager.create_backup()

    assert backup_path is not None, "Резервная копия не создана."
    assert Path(backup_path).exists(), "Файл резервной копии отсутствует."

    # Очистка тестовых данных
    for file in Path("test_backups").glob("*.db"):
        file.unlink()
    Path("test_backups").rmdir()