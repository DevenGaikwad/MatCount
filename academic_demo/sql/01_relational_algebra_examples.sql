-- SEMS ETCS302 Unit II: relational-algebra operations expressed in MySQL SQL
-- SAFETY: SAFE FOR sems_db. Read-only statements only.

USE sems_db;

-- Selection (sigma): operational inventory positions.
SELECT inventory_id, lab_id, component_id, quantity_available, inventory_status
FROM inventory
WHERE inventory_status IN ('AVAILABLE', 'LOW_STOCK');

-- Projection (pi) with duplicate elimination.
SELECT DISTINCT component_id, component_name, part_number
FROM component
ORDER BY component_name;

-- Rename (rho): aliases clarify relation and attribute roles.
SELECT c.component_id AS catalogue_component_id,
       c.component_name AS catalogue_name
FROM component AS c
ORDER BY catalogue_name;

-- Union: every laboratory participating on either side of a transfer.
SELECT source_lab_id AS participating_lab_id
FROM transfer
UNION
SELECT destination_lab_id AS participating_lab_id
FROM transfer;

-- Intersection: laboratories that have acted as both source and destination.
SELECT source_lab_id AS lab_id
FROM transfer
INTERSECT
SELECT destination_lab_id AS lab_id
FROM transfer;

-- Set difference: catalogue components with no current inventory position.
SELECT component_id
FROM component
EXCEPT
SELECT component_id
FROM inventory;

-- Cartesian product: a bounded planning grid, not a production report.
SELECT l.lab_name, cc.category_name
FROM lab AS l
CROSS JOIN component_category AS cc
ORDER BY l.lab_name, cc.category_name
LIMIT 20;

-- Theta/equi-join: component positions with their owning laboratory.
SELECT i.inventory_id, l.lab_name, c.component_name, i.quantity_available
FROM inventory AS i
JOIN lab AS l ON l.lab_id = i.lab_id
JOIN component AS c ON c.component_id = i.component_id
ORDER BY l.lab_name, c.component_name;

