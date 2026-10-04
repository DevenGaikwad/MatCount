-- SEMS optional faculty demonstration: atomic update and ROLLBACK
-- This script deliberately changes one seeded value only inside a transaction.

USE sems_db;

SELECT quantity_available INTO @sems_before_available
FROM inventory
WHERE inventory_id = 1;

START TRANSACTION;

UPDATE inventory
SET quantity_available = quantity_available + 1
WHERE inventory_id = 1;

SELECT
    inventory_id,
    @sems_before_available AS value_before_transaction,
    quantity_available AS value_inside_transaction
FROM inventory
WHERE inventory_id = 1;

ROLLBACK;

SELECT
    inventory_id,
    @sems_before_available AS expected_restored_value,
    quantity_available AS value_after_rollback,
    quantity_available = @sems_before_available AS rollback_restored_original
FROM inventory
WHERE inventory_id = 1;

