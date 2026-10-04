-- SEMS Phase 2 - Database setup
-- Target: MySQL Community Server 8.4.11 LTS
-- This script creates the full-project database only. It never uses the
-- Assignment 2/3 database smart_electronics_lab_ddl.

CREATE DATABASE IF NOT EXISTS sems_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;

USE sems_db;

-- Recommended least-privilege application account (run once as an administrator).
-- Choose a strong local password and execute these statements separately after
-- replacing the placeholder. They are intentionally commented so a password is
-- never embedded in the project history.
--
-- CREATE USER IF NOT EXISTS 'sems_app'@'localhost'
--     IDENTIFIED BY 'REPLACE_WITH_A_STRONG_LOCAL_PASSWORD';
-- GRANT SELECT, INSERT, UPDATE, DELETE, EXECUTE
--     ON sems_db.* TO 'sems_app'@'localhost';
-- FLUSH PRIVILEGES;

SELECT DATABASE() AS active_database;

