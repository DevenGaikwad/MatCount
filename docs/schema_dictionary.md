# SEMS Schema Dictionary

**Database:** `sems_db`  
**Server target:** MySQL Community Server 8.4.11 LTS  
**Relations:** exactly 13

## Master and normalized multivalued relations

### LAB

- `lab_id BIGINT UNSIGNED` — PK, AUTO_INCREMENT.
- `lab_name VARCHAR(120)` — required; unique with department.
- `department_name VARCHAR(120)` — required; unique with lab name.
- `building_name VARCHAR(120)` — required.
- `lab_type VARCHAR(60)` — required.

### LAB_CONTACT

- `lab_id BIGINT UNSIGNED` — composite PK; FK to LAB, CASCADE delete/update.
- `contact_number VARCHAR(20)` — composite PK.

### USER

- `user_id BIGINT UNSIGNED` — PK, AUTO_INCREMENT.
- `lab_id BIGINT UNSIGNED` — required FK to LAB, RESTRICT delete.
- `full_name VARCHAR(150)` — required.
- `email VARCHAR(190)` — required UNIQUE authentication mapping identifier.
- `role ENUM` — STUDENT, FACULTY, LAB_ASSISTANT, ADMINISTRATOR.
- `account_status ENUM` — ACTIVE, INACTIVE, SUSPENDED; default ACTIVE.

The raw SQL table name is quoted as `` `user` ``. No password field exists.

### USER_PHONE

- `user_id BIGINT UNSIGNED` — composite PK; FK to USER, CASCADE delete/update.
- `phone_number VARCHAR(20)` — composite PK.

### COMPONENT_CATEGORY

- `category_id BIGINT UNSIGNED` — PK, AUTO_INCREMENT.
- `category_name VARCHAR(100)` — required UNIQUE.
- `description VARCHAR(500)` — optional.

### COMPONENT

- `component_id BIGINT UNSIGNED` — PK, AUTO_INCREMENT.
- `category_id BIGINT UNSIGNED` — required FK to COMPONENT_CATEGORY, RESTRICT delete.
- `component_name VARCHAR(160)` — required.
- `part_number VARCHAR(120)` — optional UNIQUE; MySQL permits multiple NULL values.
- `specification TEXT` — optional.
- `unit_of_measure VARCHAR(30)` — required.
- `minimum_stock_level INT UNSIGNED` — required, default 0, non-negative.
- `manufacturer_details VARCHAR(255)` — optional full-project attribute.

### STORAGE_LOCATION

- `storage_location_id BIGINT UNSIGNED` — PK, AUTO_INCREMENT.
- `lab_id BIGINT UNSIGNED` — required FK to LAB, RESTRICT delete.
- `cabinet_no VARCHAR(30)` — required.
- `shelf_no VARCHAR(30)` — optional.
- `drawer_no VARCHAR(30)` — optional.
- `location_type VARCHAR(50)` — required.

Declared UNIQUE key: `(lab_id, cabinet_no, shelf_no, drawer_no, location_type)`. The service layer additionally performs null-normalized matching because MySQL UNIQUE keys allow multiple NULLs.

## Stock and workflow relations

### INVENTORY

- `inventory_id BIGINT UNSIGNED` — PK, AUTO_INCREMENT.
- `lab_id BIGINT UNSIGNED` — required FK to LAB.
- `component_id BIGINT UNSIGNED` — required FK to COMPONENT.
- `storage_location_id BIGINT UNSIGNED` — required FK to STORAGE_LOCATION.
- `quantity_available INT UNSIGNED` — free stock; default 0.
- `quantity_reserved INT UNSIGNED` — approved but undispatched stock; default 0.
- `unit_cost DECIMAL(12,2) UNSIGNED` — non-negative; default 0.00.
- `inventory_status ENUM` — AVAILABLE, LOW_STOCK, OUT_OF_STOCK, BLOCKED, INACTIVE.
- `last_updated TIMESTAMP` — automatic insert/update timestamp.

UNIQUE position: `(lab_id, component_id, storage_location_id)`. A narrow trigger plus the service layer enforce that location and inventory share the same lab.

Reporting distinguishes `available_value = quantity_available × unit_cost` from total on-hand `inventory_value = (quantity_available + quantity_reserved) × unit_cost`. Reserved stock remains physically on hand until dispatch.

### COMPONENT_REQUEST

- `request_id BIGINT UNSIGNED` — PK, AUTO_INCREMENT.
- `requesting_lab_id BIGINT UNSIGNED` — required FK to LAB.
- `created_by BIGINT UNSIGNED` — required FK to USER.
- `request_date DATE` — required.
- `required_by_date DATE` — required; not before request date.
- `priority ENUM` — LOW, MEDIUM, HIGH, URGENT.
- `reason VARCHAR(1000)` — required.
- `request_status ENUM` — DRAFT, SUBMITTED, PARTIALLY_APPROVED, APPROVED, FULFILLED, REJECTED, CANCELLED.

### REQUEST_ITEM

- `request_item_id BIGINT UNSIGNED` — PK, AUTO_INCREMENT.
- `request_id BIGINT UNSIGNED` — required FK to COMPONENT_REQUEST; controlled owned-line CASCADE.
- `component_id BIGINT UNSIGNED` — required FK to COMPONENT.
- `quantity_requested INT UNSIGNED` — positive.
- `quantity_approved INT UNSIGNED` — default 0; not above requested.
- `item_status ENUM` — PENDING, PARTIALLY_APPROVED, APPROVED, REJECTED, ALLOCATED, FULFILLED.
- `remarks VARCHAR(500)` — optional.

UNIQUE line: `(request_id, component_id)`.

### TRANSFER

- `transfer_id BIGINT UNSIGNED` — PK, AUTO_INCREMENT.
- `request_id BIGINT UNSIGNED` — required FK to COMPONENT_REQUEST.
- `source_lab_id BIGINT UNSIGNED` — required FK to LAB.
- `destination_lab_id BIGINT UNSIGNED` — required FK to LAB; must differ from source.
- `created_by BIGINT UNSIGNED` — required FK to USER.
- `received_by BIGINT UNSIGNED` — nullable FK to USER until complete receipt.
- `dispatch_date DATE` — nullable until dispatch.
- `received_date DATE` — nullable until complete receipt; not before dispatch.
- `transfer_status ENUM` — DRAFT, APPROVED, DISPATCHED, RECEIVED, PARTIALLY_RETURNED, RETURNED, CANCELLED.
- `approval_status ENUM` — PENDING, APPROVED, REJECTED.

### TRANSFER_ITEM

- `transfer_item_id BIGINT UNSIGNED` — PK, AUTO_INCREMENT.
- `transfer_id BIGINT UNSIGNED` — required FK to TRANSFER; controlled owned-line CASCADE.
- `inventory_id BIGINT UNSIGNED` — required FK to original/source INVENTORY.
- `quantity_sent INT UNSIGNED` — positive allocation/dispatch quantity.
- `quantity_received INT UNSIGNED` — default 0; not above sent.
- `return_due_date DATE` — optional; non-NULL indicates temporary sharing.
- `return_date DATE` — optional actual return date.
- `condition_on_issue VARCHAR(100)` — set only at dispatch.
- `condition_on_return VARCHAR(100)` — set only at actual return.

UNIQUE allocation: `(transfer_id, inventory_id)`. No destination-inventory attribute exists.

### DISPOSAL_RECORD

- `disposal_id BIGINT UNSIGNED` — PK, AUTO_INCREMENT.
- `inventory_id BIGINT UNSIGNED` — required FK to INVENTORY.
- `authorized_by BIGINT UNSIGNED` — required FK to USER.
- `quantity_disposed INT UNSIGNED` — positive; service ensures it does not exceed free stock.
- `disposal_date DATE` — required.
- `disposal_reason VARCHAR(500)` — required.
- `disposal_method VARCHAR(120)` — required.
- `remarks VARCHAR(500)` — optional.

## Reporting views

| View | Grain |
|---|---|
| `v_inventory_detail` | One inventory position; includes available-only and total on-hand values |
| `v_component_stock_summary` | One laboratory + component; sums available/reserved/on-hand value without line multiplication |
| `v_low_stock_components` | One low-stock laboratory + component |
| `v_request_progress` | One request header |
| `v_transfer_detail` | One transfer item |
| `v_overdue_returns` | One overdue temporary transfer item |
| `v_disposal_summary` | One disposal event |
