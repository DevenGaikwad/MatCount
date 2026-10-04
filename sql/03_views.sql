-- SEMS Phase 2 - Read-only reporting views
-- Each view documents its grain to prevent accidental double-counting.

USE sems_db;

CREATE OR REPLACE VIEW v_inventory_detail AS
SELECT
    i.inventory_id,
    i.lab_id,
    l.lab_name,
    l.department_name,
    i.component_id,
    c.component_name,
    c.part_number,
    cc.category_id,
    cc.category_name,
    i.storage_location_id,
    sl.cabinet_no,
    sl.shelf_no,
    sl.drawer_no,
    sl.location_type,
    i.quantity_available,
    i.quantity_reserved,
    i.quantity_available + i.quantity_reserved AS quantity_accounted,
    i.unit_cost,
    ROUND(i.quantity_available * i.unit_cost, 2) AS available_value,
    ROUND((i.quantity_available + i.quantity_reserved) * i.unit_cost, 2)
        AS inventory_value,
    i.inventory_status,
    i.last_updated
FROM inventory AS i
JOIN lab AS l ON l.lab_id = i.lab_id
JOIN component AS c ON c.component_id = i.component_id
JOIN component_category AS cc ON cc.category_id = c.category_id
JOIN storage_location AS sl
  ON sl.storage_location_id = i.storage_location_id;
-- Grain: one row per INVENTORY record.

CREATE OR REPLACE VIEW v_component_stock_summary AS
SELECT
    i.lab_id,
    l.lab_name,
    i.component_id,
    c.component_name,
    c.part_number,
    cc.category_name,
    c.minimum_stock_level,
    SUM(i.quantity_available) AS quantity_available,
    SUM(i.quantity_reserved) AS quantity_reserved,
    ROUND(SUM(i.quantity_available * i.unit_cost), 2) AS available_value,
    ROUND(SUM((i.quantity_available + i.quantity_reserved) * i.unit_cost), 2)
        AS inventory_value,
    COUNT(*) AS inventory_position_count
FROM inventory AS i
JOIN lab AS l ON l.lab_id = i.lab_id
JOIN component AS c ON c.component_id = i.component_id
JOIN component_category AS cc ON cc.category_id = c.category_id
WHERE i.inventory_status NOT IN ('BLOCKED', 'INACTIVE')
GROUP BY
    i.lab_id, l.lab_name, i.component_id, c.component_name,
    c.part_number, cc.category_name, c.minimum_stock_level;
-- Grain: one row per LAB + COMPONENT.

CREATE OR REPLACE VIEW v_low_stock_components AS
SELECT
    css.lab_id,
    css.lab_name,
    css.component_id,
    css.component_name,
    css.part_number,
    css.category_name,
    css.minimum_stock_level,
    css.quantity_available,
    css.quantity_reserved,
    css.minimum_stock_level - css.quantity_available AS shortage_quantity
FROM v_component_stock_summary AS css
WHERE css.quantity_available <= css.minimum_stock_level;
-- Grain: one low-stock LAB + COMPONENT combination.

CREATE OR REPLACE VIEW v_request_progress AS
SELECT
    cr.request_id,
    cr.requesting_lab_id,
    l.lab_name AS requesting_lab_name,
    cr.created_by,
    u.full_name AS created_by_name,
    cr.request_date,
    cr.required_by_date,
    cr.priority,
    cr.request_status,
    COUNT(ri.request_item_id) AS item_count,
    COALESCE(SUM(ri.quantity_requested), 0) AS total_requested,
    COALESCE(SUM(ri.quantity_approved), 0) AS total_approved,
    COALESCE(SUM(ri.item_status = 'FULFILLED'), 0) AS fulfilled_item_count,
    COALESCE(SUM(ri.item_status = 'REJECTED'), 0) AS rejected_item_count
FROM component_request AS cr
JOIN lab AS l ON l.lab_id = cr.requesting_lab_id
JOIN `user` AS u ON u.user_id = cr.created_by
LEFT JOIN request_item AS ri ON ri.request_id = cr.request_id
GROUP BY
    cr.request_id, cr.requesting_lab_id, l.lab_name, cr.created_by,
    u.full_name, cr.request_date, cr.required_by_date, cr.priority,
    cr.request_status;
-- Grain: one COMPONENT_REQUEST header.

CREATE OR REPLACE VIEW v_transfer_detail AS
SELECT
    t.transfer_id,
    t.request_id,
    t.source_lab_id,
    sl.lab_name AS source_lab_name,
    t.destination_lab_id,
    dl.lab_name AS destination_lab_name,
    t.created_by,
    cu.full_name AS created_by_name,
    t.received_by,
    ru.full_name AS received_by_name,
    t.dispatch_date,
    t.received_date,
    t.transfer_status,
    t.approval_status,
    ti.transfer_item_id,
    ti.inventory_id,
    i.component_id,
    c.component_name,
    c.part_number,
    ti.quantity_sent,
    ti.quantity_received,
    ti.return_due_date,
    ti.return_date,
    ti.condition_on_issue,
    ti.condition_on_return
FROM transfer AS t
JOIN lab AS sl ON sl.lab_id = t.source_lab_id
JOIN lab AS dl ON dl.lab_id = t.destination_lab_id
JOIN `user` AS cu ON cu.user_id = t.created_by
LEFT JOIN `user` AS ru ON ru.user_id = t.received_by
JOIN transfer_item AS ti ON ti.transfer_id = t.transfer_id
JOIN inventory AS i ON i.inventory_id = ti.inventory_id
JOIN component AS c ON c.component_id = i.component_id;
-- Grain: one TRANSFER_ITEM allocation.

CREATE OR REPLACE VIEW v_overdue_returns AS
SELECT
    vtd.transfer_id,
    vtd.transfer_item_id,
    vtd.request_id,
    vtd.source_lab_id,
    vtd.source_lab_name,
    vtd.destination_lab_id,
    vtd.destination_lab_name,
    vtd.component_id,
    vtd.component_name,
    vtd.quantity_received,
    vtd.return_due_date,
    DATEDIFF(CURRENT_DATE, vtd.return_due_date) AS days_overdue,
    vtd.transfer_status
FROM v_transfer_detail AS vtd
WHERE vtd.return_due_date < CURRENT_DATE
  AND vtd.return_date IS NULL
  AND vtd.quantity_received > 0
  AND vtd.transfer_status IN ('DISPATCHED', 'RECEIVED', 'PARTIALLY_RETURNED');
-- Grain: one overdue temporary TRANSFER_ITEM.

CREATE OR REPLACE VIEW v_disposal_summary AS
SELECT
    dr.disposal_id,
    dr.disposal_date,
    dr.inventory_id,
    i.lab_id,
    l.lab_name,
    i.component_id,
    c.component_name,
    dr.authorized_by,
    u.full_name AS authorized_by_name,
    dr.quantity_disposed,
    i.unit_cost,
    ROUND(dr.quantity_disposed * i.unit_cost, 2) AS disposed_value,
    dr.disposal_reason,
    dr.disposal_method,
    dr.remarks
FROM disposal_record AS dr
JOIN inventory AS i ON i.inventory_id = dr.inventory_id
JOIN lab AS l ON l.lab_id = i.lab_id
JOIN component AS c ON c.component_id = i.component_id
JOIN `user` AS u ON u.user_id = dr.authorized_by;
-- Grain: one DISPOSAL_RECORD event.
