-- SEMS ETCS302 Assignment 9: cursor-based row-by-row processing
-- SAFETY: ACADEMIC DEMO SCHEMA ONLY. Reads sems_db; creates a temporary table.
-- Production reporting should prefer the equivalent set-based GROUP BY query.

CREATE DATABASE IF NOT EXISTS sems_academic_demo
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

DROP PROCEDURE IF EXISTS sems_academic_demo.sp_cursor_lab_stock_summary;

DELIMITER $$

CREATE PROCEDURE sems_academic_demo.sp_cursor_lab_stock_summary()
MODIFIES SQL DATA
BEGIN
    DECLARE v_done BOOLEAN DEFAULT FALSE;
    DECLARE v_lab_id BIGINT UNSIGNED;
    DECLARE v_lab_name VARCHAR(120);
    DECLARE v_available BIGINT UNSIGNED;
    DECLARE v_reserved BIGINT UNSIGNED;

    DECLARE stock_cursor CURSOR FOR
        SELECT l.lab_id,
               l.lab_name,
               COALESCE(SUM(i.quantity_available), 0),
               COALESCE(SUM(i.quantity_reserved), 0)
        FROM sems_db.lab AS l
        LEFT JOIN sems_db.inventory AS i ON i.lab_id = l.lab_id
        GROUP BY l.lab_id, l.lab_name
        ORDER BY l.lab_id;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = TRUE;

    DROP TEMPORARY TABLE IF EXISTS cursor_stock_output;
    CREATE TEMPORARY TABLE cursor_stock_output (
        sequence_no INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        lab_id BIGINT UNSIGNED NOT NULL,
        lab_name VARCHAR(120) NOT NULL,
        quantity_available BIGINT UNSIGNED NOT NULL,
        quantity_reserved BIGINT UNSIGNED NOT NULL,
        stock_note VARCHAR(40) NOT NULL
    ) ENGINE = InnoDB;

    OPEN stock_cursor;

    stock_loop: LOOP
        FETCH stock_cursor
          INTO v_lab_id, v_lab_name, v_available, v_reserved;

        IF v_done THEN
            LEAVE stock_loop;
        END IF;

        INSERT INTO cursor_stock_output (
            lab_id, lab_name, quantity_available, quantity_reserved, stock_note
        )
        VALUES (
            v_lab_id,
            v_lab_name,
            v_available,
            v_reserved,
            CASE WHEN v_available = 0 THEN 'NO AVAILABLE STOCK'
                 ELSE 'STOCK PRESENT' END
        );
    END LOOP;

    CLOSE stock_cursor;

    SELECT sequence_no, lab_id, lab_name, quantity_available,
           quantity_reserved, stock_note
    FROM cursor_stock_output
    ORDER BY sequence_no;

    DROP TEMPORARY TABLE cursor_stock_output;
END$$

DELIMITER ;

CALL sems_academic_demo.sp_cursor_lab_stock_summary();

-- Preferred production equivalent: one set-based statement, no cursor loop.
SELECT l.lab_id, l.lab_name,
       COALESCE(SUM(i.quantity_available), 0) AS quantity_available,
       COALESCE(SUM(i.quantity_reserved), 0) AS quantity_reserved
FROM sems_db.lab AS l
LEFT JOIN sems_db.inventory AS i ON i.lab_id = l.lab_id
GROUP BY l.lab_id, l.lab_name
ORDER BY l.lab_id;
