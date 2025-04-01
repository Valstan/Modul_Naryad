# db/queries.py
REPORT_BASE_QUERY = """
SELECT 
    wo.id AS order_id,
    COALESCE(wo.order_date, 'Нет данных') AS order_date,
    COALESCE(p.name, 'Не указано') AS product,
    COALESCE(c.contract_code, 'Без контракта') AS contract_code,
    COALESCE(SUM(owt.amount), 0) AS total_amount,
    COALESCE(GROUP_CONCAT(e.full_name, ', '), 'Не выбраны') AS workers
FROM work_orders wo
LEFT JOIN products p ON wo.product_id = p.id
LEFT JOIN contracts c ON wo.contract_id = c.id
LEFT JOIN order_workers ow ON wo.id = ow.order_id
LEFT JOIN employees e ON ow.worker_id = e.id
LEFT JOIN order_work_types owt ON wo.id = owt.order_id
GROUP BY wo.id
"""

WORK_ORDERS_FOR_PDF_HTML = """
SELECT
    wo.id AS order_id,
    wo.order_date,
    p.name AS product,
    c.contract_code,
    SUM(owt.amount) AS total_amount
FROM work_orders wo
LEFT JOIN products p ON wo.product_id = p.id
LEFT JOIN contracts c ON wo.contract_id = c.id
LEFT JOIN order_work_types owt ON wo.id = owt.order_id
GROUP BY wo.id
"""