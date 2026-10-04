-- SEMS ETCS302 Unit IV: two-session row-locking / lost-update prevention
-- SAFETY: MANUAL TWO-SESSION DEMO in sems_academic_demo only.
-- Run setup once, then copy Session A and Session B blocks into separate
-- MySQL Workbench SQL Editor tabs. Do not run the entire file as one script.

CREATE DATABASE IF NOT EXISTS sems_academic_demo
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS sems_academic_demo.concurrency_stock_demo (
    demo_inventory_id INT UNSIGNED NOT NULL,
    quantity_available INT UNSIGNED NOT NULL,
    quantity_reserved INT UNSIGNED NOT NULL,
    CONSTRAINT pk_concurrency_stock_demo PRIMARY KEY (demo_inventory_id),
    CONSTRAINT ck_concurrency_nonnegative CHECK (
        quantity_available >= 0 AND quantity_reserved >= 0
    )
) ENGINE = InnoDB;

INSERT INTO sems_academic_demo.concurrency_stock_demo
    (demo_inventory_id, quantity_available, quantity_reserved)
VALUES (1, 10, 0)
ON DUPLICATE KEY UPDATE quantity_available = 10, quantity_reserved = 0;

-- SESSION A — run first and stop before COMMIT.
-- START TRANSACTION;
-- SELECT quantity_available, quantity_reserved
-- FROM sems_academic_demo.concurrency_stock_demo
-- WHERE demo_inventory_id = 1
-- FOR UPDATE;
-- UPDATE sems_academic_demo.concurrency_stock_demo
-- SET quantity_available = quantity_available - 7,
--     quantity_reserved = quantity_reserved + 7
-- WHERE demo_inventory_id = 1
--   AND quantity_available >= 7;
-- SELECT ROW_COUNT() AS session_a_reserved;
-- COMMIT;

-- SESSION B — run while Session A still holds the lock.
-- START TRANSACTION;
-- SELECT quantity_available, quantity_reserved
-- FROM sems_academic_demo.concurrency_stock_demo
-- WHERE demo_inventory_id = 1
-- FOR UPDATE;
-- UPDATE sems_academic_demo.concurrency_stock_demo
-- SET quantity_available = quantity_available - 7,
--     quantity_reserved = quantity_reserved + 7
-- WHERE demo_inventory_id = 1
--   AND quantity_available >= 7;
-- SELECT ROW_COUNT() AS session_b_reserved;
-- COMMIT;

-- Expected: Session B waits for A. After A commits, B re-reads quantity 3 and
-- its guarded UPDATE affects 0 rows. Stock is never over-allocated.

SELECT * FROM sems_academic_demo.concurrency_stock_demo;
