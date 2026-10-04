-- SEMS ETCS302 Unit IV: safe deadlock education
-- SAFETY: MANUAL TWO-SESSION DEMO in sems_academic_demo only.
-- Never run this demonstration against sems_db.

CREATE DATABASE IF NOT EXISTS sems_academic_demo
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS sems_academic_demo.deadlock_stock_demo (
    demo_inventory_id INT UNSIGNED NOT NULL,
    quantity_available INT UNSIGNED NOT NULL,
    CONSTRAINT pk_deadlock_stock_demo PRIMARY KEY (demo_inventory_id)
) ENGINE = InnoDB;

INSERT INTO sems_academic_demo.deadlock_stock_demo
    (demo_inventory_id, quantity_available)
VALUES (1, 10), (2, 20)
ON DUPLICATE KEY UPDATE quantity_available = VALUES(quantity_available);

-- SESSION A — lock row 1, then attempt row 2 after Session B locks row 2.
-- START TRANSACTION;
-- SELECT * FROM sems_academic_demo.deadlock_stock_demo
-- WHERE demo_inventory_id = 1 FOR UPDATE;
-- UPDATE sems_academic_demo.deadlock_stock_demo
-- SET quantity_available = quantity_available + 1
-- WHERE demo_inventory_id = 2;
-- COMMIT;

-- SESSION B — lock row 2, then attempt row 1 after Session A locks row 1.
-- START TRANSACTION;
-- SELECT * FROM sems_academic_demo.deadlock_stock_demo
-- WHERE demo_inventory_id = 2 FOR UPDATE;
-- UPDATE sems_academic_demo.deadlock_stock_demo
-- SET quantity_available = quantity_available + 1
-- WHERE demo_inventory_id = 1;
-- COMMIT;

-- Expected: InnoDB detects the wait cycle and rolls back one victim
-- transaction. The application must roll back/retry the complete transaction.
-- MySQL normally reports error 1213 / SQLSTATE 40001 for the chosen victim.
-- SHOW ENGINE INNODB STATUS; -- inspect only if faculty permits.

-- Prevention used by SEMS: acquire inventory locks in ascending inventory_id
-- order in every service transaction, keep transactions short and use indexes.
