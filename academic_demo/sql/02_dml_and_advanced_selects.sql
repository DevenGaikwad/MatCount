-- SEMS ETCS302 Assignment 3: DML and selection operators
-- SAFETY: SAFE FOR sems_db. Mutations affect a session-local TEMPORARY table only.

USE sems_db;

DROP TEMPORARY TABLE IF EXISTS demo_component_request_queue;

CREATE TEMPORARY TABLE demo_component_request_queue (
    demo_line_id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    component_name VARCHAR(160) NOT NULL,
    requested_quantity INT UNSIGNED NOT NULL,
    priority ENUM('LOW', 'MEDIUM', 'HIGH', 'URGENT') NOT NULL,
    review_note VARCHAR(200) NULL,
    CONSTRAINT ck_demo_requested_positive CHECK (requested_quantity > 0)
) ENGINE = InnoDB;

INSERT INTO demo_component_request_queue
    (component_name, requested_quantity, priority, review_note)
VALUES
    ('Operational Amplifier', 12, 'HIGH', NULL),
    ('Resistor 1 kOhm', 50, 'MEDIUM', 'For analogue circuits'),
    ('STM32 Microcontroller', 4, 'URGENT', 'Capstone demonstration');

UPDATE demo_component_request_queue
SET review_note = COALESCE(review_note, 'Awaiting faculty review')
WHERE priority IN ('HIGH', 'URGENT');

DELETE FROM demo_component_request_queue
WHERE priority = 'LOW';

-- Equality, range, LIKE, NULL, DISTINCT, ordering and limiting.
SELECT demo_line_id, component_name, requested_quantity, priority, review_note
FROM demo_component_request_queue
WHERE requested_quantity BETWEEN 4 AND 50
  AND component_name LIKE '%o%'
  AND review_note IS NOT NULL
ORDER BY requested_quantity DESC, component_name
LIMIT 10;

SELECT DISTINCT priority
FROM demo_component_request_queue
ORDER BY priority;

-- Explicit NULL selection before the disposable relation is removed.
SELECT demo_line_id, component_name
FROM demo_component_request_queue
WHERE review_note IS NULL;

DROP TEMPORARY TABLE demo_component_request_queue;
