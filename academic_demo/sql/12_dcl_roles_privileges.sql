-- SEMS ETCS302 Unit III: DCL, MySQL roles and least privilege
-- SAFETY: ADMINISTRATOR-ONLY DCL DEMO. Review account names and replace the
-- placeholder password locally. This script does not alter SEMS relations.

CREATE ROLE IF NOT EXISTS
    'sems_runtime_role'@'%',
    'sems_report_role'@'%',
    'sems_revoke_demo_role'@'%';

-- Runtime role: the application has no schema-definition or MySQL-user powers.
GRANT SELECT, INSERT, UPDATE
ON sems_db.*
TO 'sems_runtime_role'@'%';

GRANT EXECUTE
ON PROCEDURE sems_db.sp_component_availability
TO 'sems_runtime_role'@'%';

GRANT EXECUTE
ON FUNCTION sems_db.fn_inventory_available_value
TO 'sems_runtime_role'@'%';

-- Restricted report role: grant only non-financial reporting views.
GRANT SELECT
ON sems_db.v_low_stock_components
TO 'sems_report_role'@'%';

GRANT SELECT
ON sems_db.v_request_progress
TO 'sems_report_role'@'%';

CREATE USER IF NOT EXISTS 'sems_demo_restricted'@'localhost'
IDENTIFIED BY 'REPLACE_WITH_LOCAL_DEMO_PASSWORD';

GRANT 'sems_report_role'@'%'
TO 'sems_demo_restricted'@'localhost';

SET DEFAULT ROLE 'sems_report_role'@'%'
TO 'sems_demo_restricted'@'localhost';

SHOW GRANTS FOR 'sems_runtime_role'@'%';
SHOW GRANTS FOR 'sems_report_role'@'%';
SHOW GRANTS FOR 'sems_demo_restricted'@'localhost'
USING 'sems_report_role'@'%';

-- Explicit REVOKE demonstration on a disposable role, then restore no access.
GRANT SELECT
ON sems_db.v_low_stock_components
TO 'sems_revoke_demo_role'@'%';

REVOKE SELECT
ON sems_db.v_low_stock_components
FROM 'sems_revoke_demo_role'@'%';

SHOW GRANTS FOR 'sems_revoke_demo_role'@'%';

-- Optional cleanup after faculty evidence is captured:
-- DROP USER 'sems_demo_restricted'@'localhost';
-- DROP ROLE 'sems_runtime_role'@'%', 'sems_report_role'@'%',
--           'sems_revoke_demo_role'@'%';

-- Application USER.role values and MySQL server roles solve different layers:
-- the former controls business actions; the latter controls database accounts.

