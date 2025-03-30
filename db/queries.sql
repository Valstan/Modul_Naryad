-- Создание таблицы employees
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    workshop_number INTEGER NOT NULL,
    position TEXT NOT NULL,
    employee_id TEXT UNIQUE NOT NULL
);

-- Создание таблицы work_orders
CREATE TABLE IF NOT EXISTS work_orders (
    id INTEGER PRIMARY KEY,
    order_date TEXT NOT NULL,
    product_id INTEGER NOT NULL,
    contract_id INTEGER NOT NULL,
    total_amount REAL NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (contract_id) REFERENCES contracts(id)
);