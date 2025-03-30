# utils/validators.py
from datetime import datetime
from db.database import Database
from typing import Optional


def validate_date(date_str: str) -> bool:
    """Проверяет корректность даты в формате DD.MM.YYYY."""
    try:
        datetime.strptime(date_str, "%d.%m.%Y")
        return True
    except ValueError:
        return False


def validate_positive_integer(value: str) -> bool:
    """Проверяет, что значение является положительным целым числом."""
    try:
        number = int(value)
        return number > 0
    except ValueError:
        return False


def validate_unique_contract_code(code: str, db: Database) -> bool:
    """Проверяет уникальность шифра контракта."""
    result = db.execute_query(
        "SELECT COUNT(*) FROM contracts WHERE contract_code = ?", (code,)
    )
    return result[0][0] == 0 if result else False


def validate_unique_work_type_name(name: str, db: Database) -> bool:
    """Проверяет уникальность наименования вида работ."""
    result = db.execute_query(
        "SELECT COUNT(*) FROM work_types WHERE name = ?", (name,)
    )
    return result[0][0] == 0 if result else False


def validate_order_data(
        date: str, workers: list, works: list, db: Database
) -> tuple[bool, Optional[str]]:
    """Комплексная проверка данных наряда. Возвращает (успех, сообщение об ошибке)."""
    errors = []

    if not validate_date(date):
        errors.append("Неверный формат даты. Используйте ДД.ММ.ГГГГ")

    if not workers:
        errors.append("Выберите хотя бы одного рабочего")

    for work in works:
        if not validate_positive_integer(str(work["quantity"])):
            errors.append("Количество работ должно быть положительным числом")

    if errors:
        return (False, "\n".join(errors))
    return (True, None)


def validate_unique_employee_id(employee_id: str, db: Database) -> bool:
    """Проверяет уникальность табельного номера."""
    result = db.execute_query(
        "SELECT COUNT(*) FROM employees WHERE employee_id = ?", (employee_id,)
    )
    return result[0][0] == 0 if result else False
