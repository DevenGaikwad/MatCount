-- SEMS Phase 2 - Narrow relational invariant triggers
-- Workflow transitions remain in Python services. These triggers only ensure that
-- INVENTORY.lab_id matches its referenced STORAGE_LOCATION.lab_id.

USE sems_db;

DROP TRIGGER IF EXISTS trg_inventory_validate_location_bi;
DROP TRIGGER IF EXISTS trg_inventory_validate_location_bu;

DELIMITER $$

CREATE TRIGGER trg_inventory_validate_location_bi
BEFORE INSERT ON inventory
FOR EACH ROW
BEGIN
    DECLARE v_location_lab_id BIGINT UNSIGNED;

    SELECT lab_id
      INTO v_location_lab_id
      FROM storage_location
     WHERE storage_location_id = NEW.storage_location_id;

    IF v_location_lab_id <> NEW.lab_id THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Inventory laboratory must match storage-location laboratory';
    END IF;
END$$

CREATE TRIGGER trg_inventory_validate_location_bu
BEFORE UPDATE ON inventory
FOR EACH ROW
BEGIN
    DECLARE v_location_lab_id BIGINT UNSIGNED;

    SELECT lab_id
      INTO v_location_lab_id
      FROM storage_location
     WHERE storage_location_id = NEW.storage_location_id;

    IF v_location_lab_id <> NEW.lab_id THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Inventory laboratory must match storage-location laboratory';
    END IF;
END$$

DELIMITER ;

