-- SEMS ETCS302: view abstraction, indexes and optimizer evidence
-- SAFETY: SAFE FOR sems_db. EXPLAIN is read-only. EXPLAIN ANALYZE executes
-- the SELECT but does not mutate data.

USE sems_db;

SHOW FULL TABLES WHERE Table_type = 'VIEW';
SHOW CREATE VIEW v_inventory_detail;
SHOW INDEX FROM component;
SHOW INDEX FROM inventory;
SHOW INDEX FROM component_request;
SHOW INDEX FROM transfer;

-- 1. Component availability: prefix search can use idx_component_name.
EXPLAIN FORMAT=TREE
SELECT component_id, component_name, part_number
FROM component
WHERE component_name LIKE 'R%'
ORDER BY component_name
LIMIT 25;

-- Contrast: a leading wildcard is less index-selective and often scans more.
EXPLAIN FORMAT=TREE
SELECT component_id, component_name, part_number
FROM component
WHERE component_name LIKE '%resistor%'
ORDER BY component_name
LIMIT 25;

-- 2. Request progress queue: composite lab/status/required-date access.
EXPLAIN FORMAT=TREE
SELECT request_id, requesting_lab_id, request_status, required_by_date
FROM component_request
WHERE requesting_lab_id = 1
  AND request_status IN ('SUBMITTED', 'PARTIALLY_APPROVED', 'APPROVED')
ORDER BY required_by_date
LIMIT 50;

-- 3. Transfer operational lookup.
EXPLAIN FORMAT=TREE
SELECT transfer_id, source_lab_id, transfer_status, dispatch_date
FROM transfer
WHERE source_lab_id = 1
  AND transfer_status IN ('APPROVED', 'DISPATCHED')
ORDER BY dispatch_date DESC
LIMIT 50;

-- 4. Low-stock reporting through the documented view.
EXPLAIN FORMAT=TREE
SELECT lab_id, component_id, component_name, quantity_available,
       minimum_stock_level
FROM v_low_stock_components
WHERE lab_id = 1
ORDER BY shortage_quantity DESC
LIMIT 50;

-- Actual iterator evidence is safe for this read-only bounded SELECT.
EXPLAIN ANALYZE FORMAT=TREE
SELECT inventory_id, lab_id, component_id, quantity_available
FROM inventory
WHERE component_id = 1
  AND inventory_status IN ('AVAILABLE', 'LOW_STOCK')
ORDER BY inventory_id
LIMIT 50;

