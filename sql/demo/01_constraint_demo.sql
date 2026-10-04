-- SEMS optional faculty demonstration: expected constraint failures
-- Target: MySQL 8.4.11 / sems_db after scripts 00-06.
--
-- IMPORTANT: Select and execute ONE EXPECTED FAILURE statement at a time in
-- Workbench, then execute its following verification SELECT. Each invalid DML
-- statement is rejected before a row is changed; no cleanup data is required.

USE sems_db;

-- EXPECTED FAILURE 1: uq_component_category_name rejects a duplicate category.
INSERT INTO component_category (category_name, description)
VALUES ('Integrated Circuits', 'Intentional duplicate for faculty demonstration');

SELECT COUNT(*) AS integrated_circuits_rows_after_failure
FROM component_category
WHERE category_name = 'Integrated Circuits';

-- EXPECTED FAILURE 2: fk_lab_contact_lab rejects a missing parent LAB.
INSERT INTO lab_contact (lab_id, contact_number)
VALUES (18446744073709551615, '020-0000-0000');

SELECT COUNT(*) AS invalid_parent_contact_rows_after_failure
FROM lab_contact
WHERE lab_id = 18446744073709551615;

-- EXPECTED FAILURE 3: ck_request_item_requested_positive rejects zero quantity.
INSERT INTO request_item
    (request_id, component_id, quantity_requested, quantity_approved, item_status)
VALUES
    (1, 9, 0, 0, 'PENDING');

SELECT COUNT(*) AS invalid_zero_quantity_rows_after_failure
FROM request_item
WHERE request_id = 1 AND component_id = 9;

-- EXPECTED FAILURE 4: ck_request_item_approval_range rejects approval above request.
UPDATE request_item
SET quantity_approved = quantity_requested + 1
WHERE request_item_id = 6;

SELECT request_item_id, quantity_requested, quantity_approved
FROM request_item
WHERE request_item_id = 6;

-- EXPECTED FAILURE 5: ck_transfer_distinct_labs rejects source = destination.
INSERT INTO transfer
    (request_id, source_lab_id, destination_lab_id, created_by,
     transfer_status, approval_status)
VALUES
    (3, 1, 1, 1, 'DRAFT', 'PENDING');

SELECT COUNT(*) AS same_lab_transfer_rows_after_failure
FROM transfer
WHERE source_lab_id = destination_lab_id;

