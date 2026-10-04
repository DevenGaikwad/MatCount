-- SEMS ETCS302 Assignment 8: validation, consistency and audit triggers
-- SAFETY: ACADEMIC DEMO SCHEMA ONLY. No production table is added or changed.
-- ACADEMIC DEMONSTRATION ONLY — NOT PART OF THE 13-RELATION PRODUCTION SCHEMA.

CREATE DATABASE IF NOT EXISTS sems_academic_demo
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE sems_academic_demo;

DROP TABLE IF EXISTS inventory_audit_demo;
DROP TABLE IF EXISTS inventory_trigger_demo;

CREATE TABLE inventory_trigger_demo (
    demo_inventory_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    component_label VARCHAR(160) NOT NULL,
    quantity_available INT NOT NULL,
    stock_status ENUM('AVAILABLE', 'OUT_OF_STOCK') NOT NULL DEFAULT 'AVAILABLE',
    CONSTRAINT pk_inventory_trigger_demo PRIMARY KEY (demo_inventory_id)
) ENGINE = InnoDB;

CREATE TABLE inventory_audit_demo (
    audit_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    demo_inventory_id BIGINT UNSIGNED NOT NULL,
    old_quantity INT NOT NULL,
    new_quantity INT NOT NULL,
    changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    changed_by VARCHAR(288) NOT NULL,
    CONSTRAINT pk_inventory_audit_demo PRIMARY KEY (audit_id),
    CONSTRAINT fk_inventory_audit_demo_inventory
        FOREIGN KEY (demo_inventory_id)
        REFERENCES inventory_trigger_demo (demo_inventory_id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE = InnoDB;

DELIMITER $$

CREATE TRIGGER trg_inventory_demo_validate_bi
BEFORE INSERT ON inventory_trigger_demo
FOR EACH ROW
BEGIN
    IF NEW.quantity_available < 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Demo inventory quantity cannot be negative';
    END IF;
    SET NEW.stock_status = CASE WHEN NEW.quantity_available = 0
                                THEN 'OUT_OF_STOCK' ELSE 'AVAILABLE' END;
END$$

CREATE TRIGGER trg_inventory_demo_sync_bu
BEFORE UPDATE ON inventory_trigger_demo
FOR EACH ROW
BEGIN
    IF NEW.quantity_available < 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Demo inventory quantity cannot be negative';
    END IF;
    SET NEW.stock_status = CASE WHEN NEW.quantity_available = 0
                                THEN 'OUT_OF_STOCK' ELSE 'AVAILABLE' END;
END$$

CREATE TRIGGER trg_inventory_demo_audit_au
AFTER UPDATE ON inventory_trigger_demo
FOR EACH ROW
BEGIN
    IF NOT (OLD.quantity_available <=> NEW.quantity_available) THEN
        INSERT INTO inventory_audit_demo (
            demo_inventory_id, old_quantity, new_quantity, changed_by
        )
        VALUES (
            NEW.demo_inventory_id,
            OLD.quantity_available,
            NEW.quantity_available,
            CURRENT_USER()
        );
    END IF;
END$$

DELIMITER ;

INSERT INTO inventory_trigger_demo (component_label, quantity_available)
VALUES ('Academic Trigger Demonstration Component', 5);

UPDATE inventory_trigger_demo
SET quantity_available = 0
WHERE component_label = 'Academic Trigger Demonstration Component';

SELECT * FROM inventory_trigger_demo;
SELECT * FROM inventory_audit_demo ORDER BY audit_id;

-- Optional expected failure; run manually and then continue:
-- UPDATE inventory_trigger_demo SET quantity_available = -1 WHERE demo_inventory_id = 1;

-- Production validation evidence remains in sql/05_triggers.sql. The literal
-- audit table above is intentionally excluded from the 13-relation sems_db.
