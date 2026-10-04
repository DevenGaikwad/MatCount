-- SEMS MySQL Workbench faculty-verification queries
-- Read-only except for no-op metadata commands. Run after 00 through 06.

USE sems_db;

-- 1. Server and database identity.
SELECT VERSION() AS mysql_server_version;
SELECT DATABASE() AS current_database;

-- 2. All 13 SEMS relations.
SHOW TABLES;

-- 3. Representative table structures.
DESCRIBE inventory;
DESCRIBE component_request;
DESCRIBE transfer;

-- 4. Primary and foreign keys.
SELECT
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name,
    kcu.referenced_table_name,
    kcu.referenced_column_name
FROM information_schema.table_constraints AS tc
LEFT JOIN information_schema.key_column_usage AS kcu
  ON kcu.constraint_schema = tc.constraint_schema
 AND kcu.table_name = tc.table_name
 AND kcu.constraint_name = tc.constraint_name
WHERE tc.constraint_schema = DATABASE()
  AND tc.constraint_type IN ('PRIMARY KEY', 'FOREIGN KEY')
ORDER BY tc.table_name, tc.constraint_type, tc.constraint_name,
         kcu.ordinal_position;

-- 5. UNIQUE and CHECK constraints.
SELECT
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type,
    cc.check_clause
FROM information_schema.table_constraints AS tc
LEFT JOIN information_schema.check_constraints AS cc
  ON cc.constraint_schema = tc.constraint_schema
 AND cc.constraint_name = tc.constraint_name
WHERE tc.constraint_schema = DATABASE()
  AND tc.constraint_type IN ('UNIQUE', 'CHECK')
ORDER BY tc.table_name, tc.constraint_type, tc.constraint_name;

-- 6. Major-table record counts.
SELECT 'lab' AS relation_name, COUNT(*) AS record_count FROM lab
UNION ALL SELECT 'user', COUNT(*) FROM `user`
UNION ALL SELECT 'component', COUNT(*) FROM component
UNION ALL SELECT 'inventory', COUNT(*) FROM inventory
UNION ALL SELECT 'component_request', COUNT(*) FROM component_request
UNION ALL SELECT 'request_item', COUNT(*) FROM request_item
UNION ALL SELECT 'transfer', COUNT(*) FROM transfer
UNION ALL SELECT 'transfer_item', COUNT(*) FROM transfer_item
UNION ALL SELECT 'disposal_record', COUNT(*) FROM disposal_record;

-- 7. Inventory joined to component, laboratory and storage position.
SELECT
    inventory_id, lab_name, component_name, part_number,
    cabinet_no, shelf_no, drawer_no,
    quantity_available, quantity_reserved, inventory_status
FROM v_inventory_detail
ORDER BY lab_name, component_name, inventory_id;

-- 8. Requests with their line-item details.
SELECT
    cr.request_id, l.lab_name, cr.request_status, cr.priority,
    c.component_name, ri.quantity_requested, ri.quantity_approved,
    ri.item_status
FROM component_request AS cr
JOIN lab AS l ON l.lab_id = cr.requesting_lab_id
JOIN request_item AS ri ON ri.request_id = cr.request_id
JOIN component AS c ON c.component_id = ri.component_id
ORDER BY cr.request_id, ri.request_item_id;

-- 9. Transfers with source and destination laboratories.
SELECT
    t.transfer_id, t.request_id,
    sl.lab_name AS source_lab,
    dl.lab_name AS destination_lab,
    t.approval_status, t.transfer_status,
    t.dispatch_date, t.received_date
FROM transfer AS t
JOIN lab AS sl ON sl.lab_id = t.source_lab_id
JOIN lab AS dl ON dl.lab_id = t.destination_lab_id
ORDER BY t.transfer_id;

-- 10. Transfer-item allocation to source inventory.
SELECT
    ti.transfer_item_id, ti.transfer_id, ti.inventory_id,
    l.lab_name AS source_lab, c.component_name,
    ti.quantity_sent, ti.quantity_received,
    ti.return_due_date, ti.return_date
FROM transfer_item AS ti
JOIN inventory AS i ON i.inventory_id = ti.inventory_id
JOIN lab AS l ON l.lab_id = i.lab_id
JOIN component AS c ON c.component_id = i.component_id
ORDER BY ti.transfer_id, ti.transfer_item_id;

-- 11. Disposal history.
SELECT * FROM v_disposal_summary ORDER BY disposal_date DESC, disposal_id DESC;

-- 12-15. Required reporting views.
SELECT * FROM v_low_stock_components
ORDER BY shortage_quantity DESC, lab_name, component_name;
SELECT * FROM v_request_progress ORDER BY request_date DESC, request_id DESC;
SELECT * FROM v_transfer_detail ORDER BY transfer_id, transfer_item_id;
SELECT * FROM v_overdue_returns ORDER BY days_overdue DESC;

-- 16. Inventory valuation report.
SELECT
    lab_name,
    ROUND(SUM(inventory_value), 2) AS total_on_hand_inventory_value
FROM v_inventory_detail
GROUP BY lab_id, lab_name
ORDER BY total_on_hand_inventory_value DESC;

-- 17. Role and account-status demonstration.
SELECT
    u.user_id, u.full_name, u.email, u.role, u.account_status, l.lab_name
FROM `user` AS u
JOIN lab AS l ON l.lab_id = u.lab_id
ORDER BY u.role, u.full_name;

-- 18. Meaningful aggregate: request demand by component.
SELECT
    c.component_id,
    c.component_name,
    SUM(ri.quantity_requested) AS total_requested,
    SUM(ri.quantity_approved) AS total_approved,
    COUNT(DISTINCT ri.request_id) AS request_count
FROM request_item AS ri
JOIN component AS c ON c.component_id = ri.component_id
GROUP BY c.component_id, c.component_name
ORDER BY total_requested DESC, c.component_name;

-- 19. Complete-concept multi-table JOIN: request -> transfer -> source stock.
SELECT
    cr.request_id,
    requester.full_name AS requested_by,
    request_lab.lab_name AS requesting_lab,
    t.transfer_id,
    source_lab.lab_name AS source_lab,
    destination_lab.lab_name AS destination_lab,
    c.component_name,
    ri.quantity_requested,
    ri.quantity_approved,
    ti.quantity_sent,
    ti.quantity_received,
    t.transfer_status
FROM component_request AS cr
JOIN `user` AS requester ON requester.user_id = cr.created_by
JOIN lab AS request_lab ON request_lab.lab_id = cr.requesting_lab_id
JOIN request_item AS ri ON ri.request_id = cr.request_id
JOIN component AS c ON c.component_id = ri.component_id
LEFT JOIN transfer AS t ON t.request_id = cr.request_id
LEFT JOIN lab AS source_lab ON source_lab.lab_id = t.source_lab_id
LEFT JOIN lab AS destination_lab ON destination_lab.lab_id = t.destination_lab_id
LEFT JOIN transfer_item AS ti ON ti.transfer_id = t.transfer_id
LEFT JOIN inventory AS source_inventory
  ON source_inventory.inventory_id = ti.inventory_id
 AND source_inventory.component_id = ri.component_id
ORDER BY cr.request_id, c.component_name, t.transfer_id;

-- 20. Representative explicit/constraint indexes.
SHOW INDEX FROM inventory;
SHOW INDEX FROM component_request;
SHOW INDEX FROM transfer;

-- 21. Views, routines and triggers visible to Workbench inspection.
SHOW FULL TABLES WHERE table_type = 'VIEW';
SHOW PROCEDURE STATUS WHERE db = DATABASE();
SHOW FUNCTION STATUS WHERE db = DATABASE();
SHOW TRIGGERS;

-- 22. Read-only routine/function demonstration.
SELECT fn_inventory_available_value(5, 12.50) AS example_available_value;
CALL sp_component_availability(1, NULL);
