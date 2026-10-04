-- SEMS ETCS302 Assignment 6: nested, correlated and existence queries
-- SAFETY: SAFE FOR sems_db. Read-only statements only.

USE sems_db;

-- Non-correlated aggregate subquery: positions above the global average.
SELECT i.inventory_id, i.lab_id, i.component_id, i.quantity_available
FROM inventory AS i
WHERE i.quantity_available > (
    SELECT AVG(all_inventory.quantity_available)
    FROM inventory AS all_inventory
)
ORDER BY i.quantity_available DESC;

-- Correlated subquery: position availability below its own laboratory average.
SELECT i.inventory_id, i.lab_id, i.component_id, i.quantity_available
FROM inventory AS i
WHERE i.quantity_available < (
    SELECT AVG(lab_inventory.quantity_available)
    FROM inventory AS lab_inventory
    WHERE lab_inventory.lab_id = i.lab_id
)
ORDER BY i.lab_id, i.quantity_available;

-- IN: components appearing on unresolved request lines.
SELECT c.component_id, c.component_name, c.part_number
FROM component AS c
WHERE c.component_id IN (
    SELECT ri.component_id
    FROM request_item AS ri
    JOIN component_request AS cr ON cr.request_id = ri.request_id
    WHERE cr.request_status IN (
        'DRAFT', 'SUBMITTED', 'PARTIALLY_APPROVED', 'APPROVED'
    )
)
ORDER BY c.component_name;

-- EXISTS: laboratories with at least one unresolved request.
SELECT l.lab_id, l.lab_name
FROM lab AS l
WHERE EXISTS (
    SELECT 1
    FROM component_request AS cr
    WHERE cr.requesting_lab_id = l.lab_id
      AND cr.request_status IN (
          'DRAFT', 'SUBMITTED', 'PARTIALLY_APPROVED', 'APPROVED'
      )
)
ORDER BY l.lab_name;

-- NOT EXISTS: components that have never been requested.
SELECT c.component_id, c.component_name
FROM component AS c
WHERE NOT EXISTS (
    SELECT 1
    FROM request_item AS ri
    WHERE ri.component_id = c.component_id
)
ORDER BY c.component_name;

-- Derived table: request approval ratios without line/header double counting.
SELECT summary.request_id,
       summary.total_requested,
       summary.total_approved,
       ROUND(
           100 * summary.total_approved / NULLIF(summary.total_requested, 0),
           2
       ) AS approval_percentage
FROM (
    SELECT ri.request_id,
           SUM(ri.quantity_requested) AS total_requested,
           SUM(ri.quantity_approved) AS total_approved
    FROM request_item AS ri
    GROUP BY ri.request_id
) AS summary
ORDER BY summary.request_id;

-- CTE + window function: rank components by available stock inside each lab.
WITH component_stock AS (
    SELECT i.lab_id, i.component_id, c.component_name,
           SUM(i.quantity_available) AS available_total
    FROM inventory AS i
    JOIN component AS c ON c.component_id = i.component_id
    GROUP BY i.lab_id, i.component_id, c.component_name
)
SELECT lab_id, component_id, component_name, available_total,
       DENSE_RANK() OVER (
           PARTITION BY lab_id ORDER BY available_total DESC
       ) AS stock_rank_within_lab
FROM component_stock
ORDER BY lab_id, stock_rank_within_lab, component_name;

