# utils/validators.py
from datetime import datetime
from db.database import Database
from typing import Optional, Tuple


def validate_date(date_str: str) -> bool:
    """Проверяет корректность даты в формате DD.MM.YYYY."""
    try:
        datetime.strptime(date_str, "%d.%m.%Y")
        return True
    except ValueError:
        return False


def validate_positive_number(value: str, is_float: bool = False) -> bool:
    """Проверяет, что значение является положительным числом (целым или дробным)."""
    try:
        number = float(value) if is_float else int(value)
        return number > 0
    except (ValueError, TypeError):
        return False


def validate_unique(field: str, value: str, table: str, db: Database) -> bool:
    """Универсальная проверка уникальности значения в указанной таблице."""
    result = db.execute_query(
        f"SELECT COUNT(*) FROM {table} WHERE {field} = ?",
        (value,)
    )
    return result[0][0] == 0 if result else False


def validate_unique_employee_id(employee_id: str, db: Database) -> bool:
    """Проверяет уникальность табельного номера."""
    return validate_unique("employee_id", employee_id, "employees", db)


def validate_unique_contract_code(code: str, db: Database) -> bool:
    """Проверяет уникальность шифра контракта."""
    return validate_unique("contract_code", code, "contracts", db)


def validate_unique_work_type_name(name: str, db: Database) -> bool:
    """Проверяет уникальность наименования вида работ."""
    return validate_unique("name", name, "work_types", db)


def validate_order_data(
        date: str,
        workers: list,
        works: list,
        db: Database
) -> Tuple[bool, Optional[str]]:
    """Комплексная проверка данных наряда."""
    errors = []

    if not validate_date(date):
        errors.append("Неверный формат даты. Используйте ДД.ММ.ГГГГ")

    if not workers:
        errors.append("Выберите хотя бы одного рабочего")

    for work in works:
        if not validate_positive_number(str(work["quantity"])):
            errors.append("Количество работ должно быть положительным числом")

    return (False, "\n".join(errors)) if errors else (True, None)