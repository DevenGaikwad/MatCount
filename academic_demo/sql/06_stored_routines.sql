-- SEMS ETCS302 Assignment 7: procedures and functions
-- SAFETY: ACADEMIC DEMO SCHEMA ONLY for new routines; sems_db is read only.

CREATE DATABASE IF NOT EXISTS sems_academic_demo
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

DROP PROCEDURE IF EXISTS sems_academic_demo.sp_lab_stock_analysis;
DROP FUNCTION IF EXISTS sems_academic_demo.fn_remaining_request_quantity;

DELIMITER $$

CREATE PROCEDURE sems_academic_demo.sp_lab_stock_analysis(
    IN p_lab_id BIGINT UNSIGNED,
    IN p_low_stock_only BOOLEAN,
    OUT p_position_count INT UNSIGNED
)
READS SQL DATA
BEGIN
    SELECT COUNT(*)
      INTO p_position_count
      FROM sems_db.inventory AS i
     WHERE p_lab_id IS NULL OR i.lab_id = p_lab_id;

    IF COALESCE(p_low_stock_only, FALSE) THEN
        SELECT lab_id, lab_name, component_id, component_name,
               quantity_available, minimum_stock_level, shortage_quantity
        FROM sems_db.v_low_stock_components
        WHERE p_lab_id IS NULL OR lab_id = p_lab_id
        ORDER BY shortage_quantity DESC, component_name;
    ELSE
        SELECT lab_id, lab_name, component_id, component_name,
               quantity_available, quantity_reserved,
               CASE
                 WHEN quantity_available = 0 THEN 'OUT OF STOCK'
                 WHEN quantity_available <= minimum_stock_level THEN 'ATTENTION'
                 ELSE 'HEALTHY'
               END AS stock_health
        FROM sems_db.v_component_stock_summary
        WHERE p_lab_id IS NULL OR lab_id = p_lab_id
        ORDER BY lab_name, component_name;
    END IF;
END$$

CREATE FUNCTION sems_academic_demo.fn_remaining_request_quantity(
    p_quantity_requested INT UNSIGNED,
    p_quantity_approved INT UNSIGNED
)
RETURNS INT UNSIGNED
DETERMINISTIC
NO SQL
BEGIN
    RETURN GREATEST(
        COALESCE(p_quantity_requested, 0) - COALESCE(p_quantity_approved, 0),
        0
    );
END$$

DELIMITER ;

-- Existing production routine/function evidence.
CALL sems_db.sp_component_availability(1, NULL);
SELECT sems_db.fn_inventory_available_value(5, 12.50)
       AS available_inventory_value;

-- Demo IN, OUT, multiple parameters and conditional logic.
CALL sems_academic_demo.sp_lab_stock_analysis(1, TRUE, @position_count);
SELECT @position_count AS matching_inventory_position_count;

SELECT sems_academic_demo.fn_remaining_request_quantity(12, 7)
       AS remaining_request_quantity;

