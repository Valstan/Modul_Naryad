import sqlite3

import pytest
from pathlib import Path
from db.database import Database
from db.backup import BackupManager

TEST_DB_PATH = "test_work_orders.db"


@pytest.fixture(scope="function")
def test_db():
    """Фикстура для создания и удаления тестовой БД."""
    db_path = Path(TEST_DB_PATH)

    # Удаление старой БД
    if db_path.exists():
        db_path.unlink(missing_ok=True)

    # Создание новой БД
    db = Database()
    db.db_path = TEST_DB_PATH
    db._init_db()  # Создает файл через Path.touch()

    # Явное создание таблиц и данных
    with db.conn:
        cursor = db.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                employee_id TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                workshop_number INTEGER NOT NULL,
                position TEXT NOT NULL
            )
        """)
        cursor.execute(
            "INSERT INTO employees (employee_id, full_name, workshop_number, position) VALUES (?, ?, ?, ?)",
            ("dummy", "Тест", 0, "Тест")
        )
        db.conn.commit()

    # Закрываем соединение, чтобы файл разблокировался
    db.conn.close()

    yield db

    # Удаление БД
    if db_path.exists():
        db_path.unlink()


def test_create_tables(test_db):
    """Проверка создания таблиц."""
    # Переоткрываем соединение для теста
    test_db.conn = sqlite3.connect(TEST_DB_PATH)
    test_db.execute_query("DELETE FROM employees")

    test_db.execute_query(
        "INSERT INTO employees (employee_id, full_name, workshop_number, position) VALUES (?, ?, ?, ?)",
        ("001", "Иванов Иван", 1, "Инженер")
    )
    result = test_db.execute_query("SELECT * FROM employees")
    assert len(result) == 1, "Данные не добавлены в таблицу."
    test_db.conn.close()


def test_backup_manager(test_db):
    """Проверка создания резервных копий."""
    # Проверка существования файла БД
    assert Path(TEST_DB_PATH).exists(), "Файл БД не создан!"

    # Создание BackupManager
    manager = BackupManager(TEST_DB_PATH, backup_dir="test_backups", max_backups=2)
    backup_path = manager.create_backup()

    # Проверки
    assert backup_path is not None, "Резервная копия не создана."
    assert Path(backup_path).exists(), "Файл резервной копии отсутствует."

    # Очистка
    for file in Path("test_backups").glob("*.db"):
        file.unlink()
    Path("test_backups").rmdir()