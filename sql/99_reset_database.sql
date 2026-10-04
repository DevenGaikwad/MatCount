-- SEMS development reset guard - DESTRUCTIVE when explicitly confirmed.
-- Never run against a database containing data that has not been backed up.
--
-- Safe use in one MySQL Workbench connection:
--   1. Execute: SET @sems_reset_confirmation = 'RESET_SEMS_DB';
--   2. Select and execute this complete script.
--   3. Re-run 00_database_setup.sql through 06_seed_data.sql.
--
-- With no exact confirmation variable, this script stops before DROP DATABASE.

CREATE DATABASE IF NOT EXISTS sems_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;
USE sems_db;

DROP PROCEDURE IF EXISTS assert_sems_reset_confirmation;

DELIMITER $$
CREATE PROCEDURE assert_sems_reset_confirmation()
BEGIN
    IF COALESCE(@sems_reset_confirmation, '') <> 'RESET_SEMS_DB' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'SEMS reset blocked: set @sems_reset_confirmation exactly as documented';
    END IF;
END$$
DELIMITER ;

CALL assert_sems_reset_confirmation();
DROP PROCEDURE assert_sems_reset_confirmation;

DROP DATABASE sems_db;

SELECT 'sems_db removed; now rerun SQL scripts 00 through 06' AS reset_status;

