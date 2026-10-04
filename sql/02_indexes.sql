-- SEMS Phase 2 - Justified secondary indexes
-- PK, UNIQUE, and automatically created FK indexes are not duplicated.

USE sems_db;

-- Case-insensitive catalogue search and category/name listing.
CREATE INDEX idx_component_name
    ON component (component_name);
CREATE INDEX idx_component_category_name
    ON component (category_id, component_name);

-- Role/account filtering within a laboratory.
CREATE INDEX idx_user_lab_role_status
    ON `user` (lab_id, role, account_status);

-- Component-centric availability and low-stock reporting. The declared
-- inventory UNIQUE key already supports lab + component lookups.
CREATE INDEX idx_inventory_component_status
    ON inventory (component_id, inventory_status);
CREATE INDEX idx_inventory_status_updated
    ON inventory (inventory_status, last_updated);

-- Request queues and date-based faculty review.
CREATE INDEX idx_request_status_date
    ON component_request (request_status, request_date);
CREATE INDEX idx_request_lab_status_required
    ON component_request (requesting_lab_id, request_status, required_by_date);
CREATE INDEX idx_request_item_status
    ON request_item (item_status, component_id);

-- Transfer operational queues and laboratory scope.
CREATE INDEX idx_transfer_status_dates
    ON transfer (transfer_status, dispatch_date, received_date);
CREATE INDEX idx_transfer_approval_status
    ON transfer (approval_status, transfer_status);
CREATE INDEX idx_transfer_source_status
    ON transfer (source_lab_id, transfer_status);
CREATE INDEX idx_transfer_destination_status
    ON transfer (destination_lab_id, transfer_status);
CREATE INDEX idx_transfer_item_overdue
    ON transfer_item (return_due_date, return_date, transfer_id);

-- Lifecycle reporting by event date.
CREATE INDEX idx_disposal_date_inventory
    ON disposal_record (disposal_date, inventory_id);

