-- SEMS optional faculty demonstration: indexes and EXPLAIN
-- EXPLAIN reports the optimizer plan; it does not execute or mutate these queries.

USE sems_db;

SHOW INDEX FROM component;
SHOW INDEX FROM inventory;
SHOW INDEX FROM component_request;
SHOW INDEX FROM transfer;

-- Availability lookup: joins PK/FK keys and filters by laboratory/status.
EXPLAIN
SELECT
    i.inventory_id, c.component_name,
    i.quantity_available, i.quantity_reserved
FROM inventory AS i
JOIN component AS c ON c.component_id = i.component_id
WHERE i.lab_id = 1
  AND i.inventory_status IN ('AVAILABLE', 'LOW_STOCK')
ORDER BY c.component_name;

-- Faculty request queue: composite request status/date index is relevant.
EXPLAIN
SELECT request_id, requesting_lab_id, request_date, required_by_date, priority
FROM component_request
WHERE request_status IN ('SUBMITTED', 'PARTIALLY_APPROVED')
ORDER BY request_date DESC;

-- Laboratory transfer queue: separate source/destination indexes can support the OR.
EXPLAIN
SELECT transfer_id, source_lab_id, destination_lab_id, transfer_status
FROM transfer
WHERE transfer_status IN ('APPROVED', 'DISPATCHED')
  AND (source_lab_id = 1 OR destination_lab_id = 1);

-- Overdue-return predicate: return_due_date leads the supporting line index.
EXPLAIN
SELECT transfer_item_id, transfer_id, return_due_date
FROM transfer_item
WHERE return_due_date < CURRENT_DATE
  AND return_date IS NULL;

