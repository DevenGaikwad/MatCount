-- SEMS ETCS302 Assignment 4: joins, scalar functions and aggregation
-- SAFETY: SAFE FOR sems_db. Read-only statements only.

USE sems_db;

-- INNER JOIN: inventory positions that have complete master-data parents.
SELECT i.inventory_id, l.lab_name, c.component_name,
       CONCAT(sl.cabinet_no, '/', COALESCE(sl.shelf_no, 'NA'), '/',
              COALESCE(sl.drawer_no, 'NA')) AS storage_coordinate,
       i.quantity_available
FROM inventory AS i
INNER JOIN lab AS l ON l.lab_id = i.lab_id
INNER JOIN component AS c ON c.component_id = i.component_id
INNER JOIN storage_location AS sl
        ON sl.storage_location_id = i.storage_location_id
ORDER BY l.lab_name, c.component_name;

-- LEFT JOIN: retain catalogue components even when no inventory exists.
SELECT c.component_id, c.component_name,
       COALESCE(SUM(i.quantity_available), 0) AS total_available
FROM component AS c
LEFT JOIN inventory AS i ON i.component_id = c.component_id
GROUP BY c.component_id, c.component_name
ORDER BY c.component_name;

-- RIGHT JOIN: retain every laboratory, including laboratories with no stock.
-- LEFT JOIN is usually clearer; RIGHT JOIN is shown because the syllabus asks.
SELECT l.lab_id, l.lab_name, COUNT(i.inventory_id) AS inventory_position_count
FROM inventory AS i
RIGHT JOIN lab AS l ON l.lab_id = i.lab_id
GROUP BY l.lab_id, l.lab_name
ORDER BY l.lab_name;

-- Same LAB relation joined twice under source/destination role aliases.
SELECT t.transfer_id,
       source_lab.lab_name AS source_laboratory,
       destination_lab.lab_name AS destination_laboratory,
       t.transfer_status
FROM transfer AS t
JOIN lab AS source_lab ON source_lab.lab_id = t.source_lab_id
JOIN lab AS destination_lab ON destination_lab.lab_id = t.destination_lab_id
ORDER BY t.transfer_id;

-- COUNT, SUM, AVG, MIN, MAX, GROUP BY and HAVING at LAB + COMPONENT grain.
SELECT l.lab_id, l.lab_name, c.component_id, c.component_name,
       COUNT(i.inventory_id) AS position_count,
       SUM(i.quantity_available) AS available_total,
       ROUND(AVG(i.quantity_available), 2) AS average_per_position,
       MIN(i.quantity_available) AS minimum_position_quantity,
       MAX(i.quantity_available) AS maximum_position_quantity
FROM inventory AS i
JOIN lab AS l ON l.lab_id = i.lab_id
JOIN component AS c ON c.component_id = i.component_id
GROUP BY l.lab_id, l.lab_name, c.component_id, c.component_name
HAVING SUM(i.quantity_available) > 0
ORDER BY available_total DESC, l.lab_name, c.component_name;

-- Date, numeric and conditional scalar expressions.
SELECT cr.request_id,
       UPPER(cr.priority) AS priority_label,
       DATEDIFF(cr.required_by_date, cr.request_date) AS lead_days,
       CASE
         WHEN cr.request_status IN ('FULFILLED', 'REJECTED', 'CANCELLED')
           THEN 'CLOSED'
         ELSE 'OPEN'
       END AS lifecycle_group
FROM component_request AS cr
ORDER BY cr.request_date DESC, cr.request_id DESC;

