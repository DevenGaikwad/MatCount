-- SEMS ETCS302 Unit IV: COMMIT, ROLLBACK, SAVEPOINT and atomicity
-- SAFETY: ACADEMIC DEMO SCHEMA ONLY.

CREATE DATABASE IF NOT EXISTS sems_academic_demo
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE sems_academic_demo;

CREATE TABLE IF NOT EXISTS transaction_stock_demo (
    demo_inventory_id INT UNSIGNED NOT NULL,
    quantity_available INT UNSIGNED NOT NULL,
    quantity_reserved INT UNSIGNED NOT NULL,
    CONSTRAINT pk_transaction_stock_demo PRIMARY KEY (demo_inventory_id),
    CONSTRAINT ck_transaction_demo_accounting CHECK (
        quantity_available >= 0 AND quantity_reserved >= 0
    )
) ENGINE = InnoDB;

INSERT INTO transaction_stock_demo
    (demo_inventory_id, quantity_available, quantity_reserved)
VALUES (1, 20, 0)
ON DUPLICATE KEY UPDATE
    quantity_available = VALUES(quantity_available),
    quantity_reserved = VALUES(quantity_reserved);

START TRANSACTION;

SELECT demo_inventory_id, quantity_available, quantity_reserved
FROM transaction_stock_demo
WHERE demo_inventory_id = 1
FOR UPDATE;

UPDATE transaction_stock_demo
SET quantity_available = quantity_available - 5,
    quantity_reserved = quantity_reserved + 5
WHERE demo_inventory_id = 1
  AND quantity_available >= 5;

SAVEPOINT after_valid_reservation;

-- Simulate a later step that faculty decides to undo.
UPDATE transaction_stock_demo
SET quantity_available = quantity_available - 3,
    quantity_reserved = quantity_reserved + 3
WHERE demo_inventory_id = 1
  AND quantity_available >= 3;

SELECT * FROM transaction_stock_demo;

ROLLBACK TO SAVEPOINT after_valid_reservation;
RELEASE SAVEPOINT after_valid_reservation;

SELECT * FROM transaction_stock_demo;

COMMIT;

-- Full rollback demonstration.
START TRANSACTION;
UPDATE transaction_stock_demo
SET quantity_available = quantity_available + 100
WHERE demo_inventory_id = 1;
SELECT * FROM transaction_stock_demo;
ROLLBACK;
SELECT * FROM transaction_stock_demo;

