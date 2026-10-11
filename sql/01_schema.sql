-- SEMS Phase 2 - Frozen relational schema (13 relations)
-- Target: MySQL Community Server 8.4.11 LTS / InnoDB / utf8mb4
-- Prerequisite: run 00_database_setup.sql.

USE sems_db;

CREATE TABLE lab (
    lab_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    lab_name VARCHAR(120) NOT NULL,
    department_name VARCHAR(120) NOT NULL,
    building_name VARCHAR(120) NOT NULL,
    lab_type VARCHAR(60) NOT NULL,
    CONSTRAINT pk_lab PRIMARY KEY (lab_id),
    CONSTRAINT uq_lab_name_department UNIQUE (lab_name, department_name)
) ENGINE = InnoDB;

CREATE TABLE lab_contact (
    lab_id BIGINT UNSIGNED NOT NULL,
    contact_number VARCHAR(20) NOT NULL,
    CONSTRAINT pk_lab_contact PRIMARY KEY (lab_id, contact_number),
    CONSTRAINT fk_lab_contact_lab
        FOREIGN KEY (lab_id) REFERENCES lab (lab_id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE `user` (
    user_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    lab_id BIGINT UNSIGNED NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(190) NOT NULL,
    role ENUM('STUDENT', 'FACULTY', 'LAB_ASSISTANT', 'ADMINISTRATOR') NOT NULL,
    account_status ENUM('ACTIVE', 'INACTIVE', 'SUSPENDED') NOT NULL DEFAULT 'ACTIVE',
    CONSTRAINT pk_user PRIMARY KEY (user_id),
    CONSTRAINT uq_user_email UNIQUE (email),
    CONSTRAINT fk_user_lab
        FOREIGN KEY (lab_id) REFERENCES lab (lab_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE user_phone (
    user_id BIGINT UNSIGNED NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    CONSTRAINT pk_user_phone PRIMARY KEY (user_id, phone_number),
    CONSTRAINT fk_user_phone_user
        FOREIGN KEY (user_id) REFERENCES `user` (user_id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE component_category (
    category_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    category_name VARCHAR(100) NOT NULL,
    description VARCHAR(500) NULL,
    CONSTRAINT pk_component_category PRIMARY KEY (category_id),
    CONSTRAINT uq_component_category_name UNIQUE (category_name)
) ENGINE = InnoDB;

CREATE TABLE component (
    component_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    category_id BIGINT UNSIGNED NOT NULL,
    component_name VARCHAR(160) NOT NULL,
    part_number VARCHAR(120) NULL,
    specification TEXT NULL,
    unit_of_measure VARCHAR(30) NOT NULL,
    minimum_stock_level INT UNSIGNED NOT NULL DEFAULT 0,
    manufacturer_details VARCHAR(255) NULL,
    CONSTRAINT pk_component PRIMARY KEY (component_id),
    CONSTRAINT uq_component_part_number UNIQUE (part_number),
    CONSTRAINT ck_component_minimum_stock CHECK (minimum_stock_level >= 0),
    CONSTRAINT fk_component_category
        FOREIGN KEY (category_id) REFERENCES component_category (category_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE storage_location (
    storage_location_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    lab_id BIGINT UNSIGNED NOT NULL,
    cabinet_no VARCHAR(30) NOT NULL,
    shelf_no VARCHAR(30) NULL,
    drawer_no VARCHAR(30) NULL,
    location_type VARCHAR(50) NOT NULL,
    CONSTRAINT pk_storage_location PRIMARY KEY (storage_location_id),
    CONSTRAINT uq_storage_coordinate
        UNIQUE (lab_id, cabinet_no, shelf_no, drawer_no, location_type),
    CONSTRAINT fk_storage_location_lab
        FOREIGN KEY (lab_id) REFERENCES lab (lab_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE inventory (
    inventory_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    lab_id BIGINT UNSIGNED NOT NULL,
    component_id BIGINT UNSIGNED NOT NULL,
    storage_location_id BIGINT UNSIGNED NOT NULL,
    quantity_available INT UNSIGNED NOT NULL DEFAULT 0,
    quantity_reserved INT UNSIGNED NOT NULL DEFAULT 0,
    unit_cost DECIMAL(12, 2) UNSIGNED NOT NULL DEFAULT 0.00,
    inventory_status ENUM(
        'AVAILABLE', 'LOW_STOCK', 'OUT_OF_STOCK', 'BLOCKED', 'INACTIVE'
    ) NOT NULL DEFAULT 'AVAILABLE',
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT pk_inventory PRIMARY KEY (inventory_id),
    CONSTRAINT uq_inventory_position
        UNIQUE (lab_id, component_id, storage_location_id),
    CONSTRAINT ck_inventory_available_nonnegative CHECK (quantity_available >= 0),
    CONSTRAINT ck_inventory_reserved_nonnegative CHECK (quantity_reserved >= 0),
    CONSTRAINT ck_inventory_unit_cost_nonnegative CHECK (unit_cost >= 0),
    CONSTRAINT fk_inventory_lab
        FOREIGN KEY (lab_id) REFERENCES lab (lab_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_inventory_component
        FOREIGN KEY (component_id) REFERENCES component (component_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_inventory_storage_location
        FOREIGN KEY (storage_location_id)
        REFERENCES storage_location (storage_location_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE component_request (
    request_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    requesting_lab_id BIGINT UNSIGNED NOT NULL,
    created_by BIGINT UNSIGNED NOT NULL,
    request_date DATE NOT NULL,
    required_by_date DATE NOT NULL,
    priority ENUM('LOW', 'MEDIUM', 'HIGH', 'URGENT') NOT NULL DEFAULT 'MEDIUM',
    reason VARCHAR(1000) NOT NULL,
    request_status ENUM(
        'DRAFT', 'SUBMITTED', 'PARTIALLY_APPROVED', 'APPROVED',
        'FULFILLED', 'REJECTED', 'CANCELLED'
    ) NOT NULL DEFAULT 'DRAFT',
    CONSTRAINT pk_component_request PRIMARY KEY (request_id),
    CONSTRAINT ck_component_request_dates CHECK (required_by_date >= request_date),
    CONSTRAINT fk_component_request_lab
        FOREIGN KEY (requesting_lab_id) REFERENCES lab (lab_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_component_request_creator
        FOREIGN KEY (created_by) REFERENCES `user` (user_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE request_item (
    request_item_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    request_id BIGINT UNSIGNED NOT NULL,
    component_id BIGINT UNSIGNED NOT NULL,
    quantity_requested INT UNSIGNED NOT NULL,
    quantity_approved INT UNSIGNED NOT NULL DEFAULT 0,
    item_status ENUM(
        'PENDING', 'PARTIALLY_APPROVED', 'APPROVED',
        'REJECTED', 'ALLOCATED', 'FULFILLED'
    ) NOT NULL DEFAULT 'PENDING',
    remarks VARCHAR(500) NULL,
    CONSTRAINT pk_request_item PRIMARY KEY (request_item_id),
    CONSTRAINT uq_request_item_component UNIQUE (request_id, component_id),
    CONSTRAINT ck_request_item_requested_positive CHECK (quantity_requested > 0),
    CONSTRAINT ck_request_item_approval_range
        CHECK (quantity_approved <= quantity_requested),
    CONSTRAINT fk_request_item_request
        FOREIGN KEY (request_id) REFERENCES component_request (request_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_request_item_component
        FOREIGN KEY (component_id) REFERENCES component (component_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE transfer (
    transfer_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    request_id BIGINT UNSIGNED NOT NULL,
    source_lab_id BIGINT UNSIGNED NOT NULL,
    destination_lab_id BIGINT UNSIGNED NOT NULL,
    created_by BIGINT UNSIGNED NOT NULL,
    received_by BIGINT UNSIGNED NULL,
    dispatch_date DATE NULL,
    received_date DATE NULL,
    transfer_status ENUM(
        'DRAFT', 'APPROVED', 'DISPATCHED', 'RECEIVED',
        'PARTIALLY_RETURNED', 'RETURNED', 'CANCELLED'
    ) NOT NULL DEFAULT 'DRAFT',
    approval_status ENUM('PENDING', 'APPROVED', 'REJECTED')
        NOT NULL DEFAULT 'PENDING',
    CONSTRAINT pk_transfer PRIMARY KEY (transfer_id),
    CONSTRAINT ck_transfer_distinct_labs CHECK (source_lab_id <> destination_lab_id),
    CONSTRAINT ck_transfer_received_after_dispatch
        CHECK (received_date IS NULL OR
               (dispatch_date IS NOT NULL AND received_date >= dispatch_date)),
    CONSTRAINT ck_transfer_receipt_pair
        CHECK ((received_by IS NULL AND received_date IS NULL) OR
               (received_by IS NOT NULL AND received_date IS NOT NULL)),
    CONSTRAINT fk_transfer_request
        FOREIGN KEY (request_id) REFERENCES component_request (request_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_transfer_source_lab
        FOREIGN KEY (source_lab_id) REFERENCES lab (lab_id),
    CONSTRAINT fk_transfer_destination_lab
        FOREIGN KEY (destination_lab_id) REFERENCES lab (lab_id),
    CONSTRAINT fk_transfer_creator
        FOREIGN KEY (created_by) REFERENCES `user` (user_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_transfer_receiver
        FOREIGN KEY (received_by) REFERENCES `user` (user_id)
) ENGINE = InnoDB;

CREATE TABLE transfer_item (
    transfer_item_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    transfer_id BIGINT UNSIGNED NOT NULL,
    inventory_id BIGINT UNSIGNED NOT NULL,
    quantity_sent INT UNSIGNED NOT NULL,
    quantity_received INT UNSIGNED NOT NULL DEFAULT 0,
    return_due_date DATE NULL,
    return_date DATE NULL,
    condition_on_issue VARCHAR(100) NULL,
    condition_on_return VARCHAR(100) NULL,
    CONSTRAINT pk_transfer_item PRIMARY KEY (transfer_item_id),
    CONSTRAINT uq_transfer_item_inventory UNIQUE (transfer_id, inventory_id),
    CONSTRAINT ck_transfer_item_sent_positive CHECK (quantity_sent > 0),
    CONSTRAINT ck_transfer_item_received_range
        CHECK (quantity_received <= quantity_sent),
    CONSTRAINT ck_transfer_item_return_date
        CHECK (return_date IS NULL OR return_due_date IS NOT NULL),
    CONSTRAINT fk_transfer_item_transfer
        FOREIGN KEY (transfer_id) REFERENCES transfer (transfer_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_transfer_item_inventory
        FOREIGN KEY (inventory_id) REFERENCES inventory (inventory_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE disposal_record (
    disposal_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    inventory_id BIGINT UNSIGNED NOT NULL,
    authorized_by BIGINT UNSIGNED NOT NULL,
    quantity_disposed INT UNSIGNED NOT NULL,
    disposal_date DATE NOT NULL,
    disposal_reason VARCHAR(500) NOT NULL,
    disposal_method VARCHAR(120) NOT NULL,
    remarks VARCHAR(500) NULL,
    CONSTRAINT pk_disposal_record PRIMARY KEY (disposal_id),
    CONSTRAINT ck_disposal_quantity_positive CHECK (quantity_disposed > 0),
    CONSTRAINT fk_disposal_inventory
        FOREIGN KEY (inventory_id) REFERENCES inventory (inventory_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_disposal_authorizer
        FOREIGN KEY (authorized_by) REFERENCES `user` (user_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE = InnoDB;

SELECT COUNT(*) AS sems_relation_count
FROM information_schema.tables
WHERE table_schema = 'sems_db'
  AND table_type = 'BASE TABLE';

