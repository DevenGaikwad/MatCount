-- SEMS ETCS302 Assignment 2: safe DDL and MySQL vendor equivalents
-- SAFETY: ACADEMIC DEMO SCHEMA ONLY. Never point this script at sems_db.
-- Target: MySQL Community Server 8.4.11 LTS.

CREATE DATABASE IF NOT EXISTS sems_academic_demo
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE sems_academic_demo;

DROP TABLE IF EXISTS ddl_component_demo;

CREATE TABLE ddl_component_demo (
    demo_component_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    part_number VARCHAR(120) NOT NULL,
    component_name VARCHAR(160) NOT NULL,
    quantity_available INT UNSIGNED NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_ddl_component_demo PRIMARY KEY (demo_component_id),
    CONSTRAINT uq_ddl_component_demo_part UNIQUE (part_number),
    CONSTRAINT ck_ddl_component_demo_quantity CHECK (quantity_available >= 0)
) ENGINE = InnoDB;

CREATE INDEX idx_ddl_component_demo_name
    ON ddl_component_demo (component_name);

-- ALTER is deliberately demonstrated only on the disposable demo relation.
ALTER TABLE ddl_component_demo
    ADD COLUMN unit_of_measure VARCHAR(30) NOT NULL DEFAULT 'piece';

DESCRIBE ddl_component_demo;
SHOW CREATE TABLE ddl_component_demo;

-- MySQL identity equivalent: AUTO_INCREMENT, as used above and in sems_db.
-- MySQL 8.4 has no standalone SQL-standard CREATE SEQUENCE object for this use.
-- MySQL 8.4 has no CREATE SYNONYM statement. A VIEW can provide a named
-- abstraction, but SEMS does not falsely claim that a view is a full synonym.
CREATE OR REPLACE VIEW v_ddl_component_demo_alias AS
SELECT demo_component_id, part_number, component_name, quantity_available
FROM ddl_component_demo;

SELECT demo_component_id, part_number, component_name, quantity_available
FROM v_ddl_component_demo_alias;

-- MySQL 8.4 has no CREATE ASSERTION. CHECK/FK/UNIQUE/triggers/services enforce
-- the corresponding business rules.

-- DROP is safe here because this is an isolated disposable teaching table.
DROP VIEW v_ddl_component_demo_alias;
DROP TABLE ddl_component_demo;
