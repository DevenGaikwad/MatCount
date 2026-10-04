-- SEMS Phase 2 - Limited academically useful routines

USE sems_db;

DROP FUNCTION IF EXISTS fn_inventory_available_value;
DROP PROCEDURE IF EXISTS sp_component_availability;

DELIMITER $$

CREATE FUNCTION fn_inventory_available_value(
    p_quantity_available INT UNSIGNED,
    p_unit_cost DECIMAL(12, 2) UNSIGNED
)
RETURNS DECIMAL(18, 2)
DETERMINISTIC
NO SQL
BEGIN
    RETURN ROUND(COALESCE(p_quantity_available, 0) * COALESCE(p_unit_cost, 0), 2);
END$$

CREATE PROCEDURE sp_component_availability(
    IN p_component_id BIGINT UNSIGNED,
    IN p_lab_id BIGINT UNSIGNED
)
READS SQL DATA
BEGIN
    SELECT
        inventory_id,
        lab_id,
        lab_name,
        component_id,
        component_name,
        part_number,
        storage_location_id,
        cabinet_no,
        shelf_no,
        drawer_no,
        quantity_available,
        quantity_reserved,
        inventory_status
    FROM v_inventory_detail
    WHERE component_id = p_component_id
      AND (p_lab_id IS NULL OR lab_id = p_lab_id)
    ORDER BY lab_name, cabinet_no, shelf_no, drawer_no;
END$$

DELIMITER ;

