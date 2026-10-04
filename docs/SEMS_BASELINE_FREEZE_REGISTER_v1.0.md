# SEMS BASELINE v1.0 — FROZEN FOR IMPLEMENTATION

**Formal project title:** Centralized Electronic Component and Laboratory Asset Management System  
**Operational name:** Smart Electronics Management System (SEMS)  
**Baseline version:** 1.0  
**Freeze date:** 2026-08-21  
**Database target:** MySQL Community Server 8.4.11 LTS  
**Status:** FROZEN FOR IMPLEMENTATION  
**Last verified completed phase:** Phase 1 — Requirements / Schema Freeze

> **Freeze consequence:** No later implementation step may add, delete, rename, merge or split a frozen core relation or attribute; change a primary key, foreign-key direction, cardinality or participation rule; or activate a future-scope module without an explicit, versioned schema decision approved by the user.

## 1. Authority and purpose

This register is the authoritative implementation baseline created after the Project Workspace Recovery Audit. It converts the accepted Phase 0 audit and the current recovery directive into a formal freeze.

Conflict priority:

1. Current explicit user instruction.
2. SEMS Project Source-of-Truth and Decision Register.
3. Latest SEMS Project Initialization Audit, except where corrected here.
4. Comprehensive Master Project Document.
5. Validated relationship/cardinality/FK decisions.
6. Final ER/EER specification recorded in authoritative documents.
7. Faculty guide/rubric.
8. Final project PPT requirements.
9. Executable SEMS ChatGPT Plus Master Prompt.
10. Assignment 2/3 material only for coursework continuity.

Duplicate TXT/DOCX/PDF/ZIP renderings are not independent authorities.

## 2. Project definition and academic boundary

SEMS is a centralized DBMS and role-aware Streamlit application for visibility and control of electronic components across engineering laboratories. It maintains laboratory, user, catalogue, storage and inventory data; supports multi-line component requests; controls inter-laboratory reservation, transfer, receipt and temporary return; records authorized disposal; and provides schema-supported analytics and CSV exports.

It must demonstrate relational modelling, normalization, PK/FK integrity, candidate/unique keys, associative entities, constraints, indexes, views, transactions, row locking, RBAC, parameterized access, reporting, exception handling and testing. It remains one modular academic application—not an ERP, microservice platform or speculative AI system.

## 3. Frozen relational boundary

The MVP contains exactly 13 relations:

1. LAB
2. LAB_CONTACT
3. USER
4. USER_PHONE
5. COMPONENT_CATEGORY
6. COMPONENT
7. STORAGE_LOCATION
8. INVENTORY
9. COMPONENT_REQUEST
10. REQUEST_ITEM
11. TRANSFER
12. TRANSFER_ITEM
13. DISPOSAL_RECORD

The 11 principal domain/workflow entities are supplemented by LAB_CONTACT and USER_PHONE to normalize multivalued attributes.

## 4. Frozen relation and attribute register

### 4.1 LAB

| Attribute | Type baseline | Null | Key/default | Rule |
|---|---|---:|---|---|
| `lab_id` | `BIGINT UNSIGNED` | No | PK, AUTO_INCREMENT | Surrogate laboratory identifier |
| `lab_name` | `VARCHAR(120)` | No | Part of UNIQUE | Human-readable name |
| `department_name` | `VARCHAR(120)` | No | Part of UNIQUE | Academic department |
| `building_name` | `VARCHAR(120)` | No | — | Campus/building context |
| `lab_type` | `VARCHAR(60)` | No | — | Laboratory classification |

Constraint: `UNIQUE (lab_name, department_name)`. LAB has no activation/status attribute. Deactivation is not an MVP feature.

### 4.2 LAB_CONTACT

| Attribute | Type baseline | Null | Key/default | Rule |
|---|---|---:|---|---|
| `lab_id` | `BIGINT UNSIGNED` | No | PK/FK → LAB | Owning laboratory |
| `contact_number` | `VARCHAR(20)` | No | PK | One normalized contact value |

Composite PK: `(lab_id, contact_number)`. Deletion may cascade only because this is an owned multivalued attribute relation.

### 4.3 USER

| Attribute | Type baseline | Null | Key/default | Rule |
|---|---|---:|---|---|
| `user_id` | `BIGINT UNSIGNED` | No | PK, AUTO_INCREMENT | Authorized participant identifier |
| `lab_id` | `BIGINT UNSIGNED` | No | FK → LAB | Every user belongs to one lab |
| `full_name` | `VARCHAR(150)` | No | — | User's name |
| `email` | `VARCHAR(190)` | No | UNIQUE | Authentication mapping/business identifier |
| `role` | ENUM | No | — | `STUDENT`, `FACULTY`, `LAB_ASSISTANT`, `ADMINISTRATOR` |
| `account_status` | ENUM | No | `ACTIVE` | `ACTIVE`, `INACTIVE`, `SUSPENDED` |

`USER` is a MySQL keyword and must be quoted as `` `user` `` in raw SQL or mapped safely through SQLAlchemy. No `password_hash` column is added.

### 4.4 USER_PHONE

| Attribute | Type baseline | Null | Key/default | Rule |
|---|---|---:|---|---|
| `user_id` | `BIGINT UNSIGNED` | No | PK/FK → USER | Owning user |
| `phone_number` | `VARCHAR(20)` | No | PK | One normalized phone value |

Composite PK: `(user_id, phone_number)`. Deletion may cascade only because this is an owned multivalued attribute relation.

### 4.5 COMPONENT_CATEGORY

| Attribute | Type baseline | Null | Key/default | Rule |
|---|---|---:|---|---|
| `category_id` | `BIGINT UNSIGNED` | No | PK, AUTO_INCREMENT | Category identifier |
| `category_name` | `VARCHAR(100)` | No | UNIQUE | Stable category name |
| `description` | `VARCHAR(500)` | Yes | — | Optional explanation |

### 4.6 COMPONENT

| Attribute | Type baseline | Null | Key/default | Rule |
|---|---|---:|---|---|
| `component_id` | `BIGINT UNSIGNED` | No | PK, AUTO_INCREMENT | Catalogue identifier |
| `category_id` | `BIGINT UNSIGNED` | No | FK → COMPONENT_CATEGORY | Mandatory classification |
| `component_name` | `VARCHAR(160)` | No | — | Human-readable component name |
| `part_number` | `VARCHAR(120)` | Yes | UNIQUE | Nullable manufacturer/business identifier |
| `specification` | `TEXT` | Yes | — | Technical specification |
| `unit_of_measure` | `VARCHAR(30)` | No | — | Unit such as piece, metre or packet |
| `minimum_stock_level` | `INT UNSIGNED` | No | `0` | Non-negative threshold |
| `manufacturer_details` | `VARCHAR(255)` | Yes | — | Full-project manufacturer attribute |

The Assignment 2/3 name `manufacturer_info` is not used in the full MVP schema.

### 4.7 STORAGE_LOCATION

| Attribute | Type baseline | Null | Key/default | Rule |
|---|---|---:|---|---|
| `storage_location_id` | `BIGINT UNSIGNED` | No | PK, AUTO_INCREMENT | Storage identifier |
| `lab_id` | `BIGINT UNSIGNED` | No | FK → LAB | Owning laboratory |
| `cabinet_no` | `VARCHAR(30)` | No | Part of UNIQUE | Cabinet identifier |
| `shelf_no` | `VARCHAR(30)` | Yes | Part of UNIQUE | Optional shelf |
| `drawer_no` | `VARCHAR(30)` | Yes | Part of UNIQUE | Optional drawer |
| `location_type` | `VARCHAR(50)` | No | Part of UNIQUE | Cabinet/shelf/drawer/bin type |

Declared constraint: `UNIQUE (lab_id, cabinet_no, shelf_no, drawer_no, location_type)`. Because MySQL permits multiple NULLs in UNIQUE keys, the service layer must also perform null-normalized duplicate-coordinate validation. This is an implementation safeguard, not a schema expansion.

### 4.8 INVENTORY

| Attribute | Type baseline | Null | Key/default | Rule |
|---|---|---:|---|---|
| `inventory_id` | `BIGINT UNSIGNED` | No | PK, AUTO_INCREMENT | Stock-record identifier |
| `lab_id` | `BIGINT UNSIGNED` | No | FK → LAB | Laboratory ownership |
| `component_id` | `BIGINT UNSIGNED` | No | FK → COMPONENT | Held component |
| `storage_location_id` | `BIGINT UNSIGNED` | No | FK → STORAGE_LOCATION | Physical coordinate |
| `quantity_available` | `INT UNSIGNED` | No | `0` | Physical stock free for a new allocation |
| `quantity_reserved` | `INT UNSIGNED` | No | `0` | Approved transfer stock not yet dispatched |
| `unit_cost` | `DECIMAL(12,2) UNSIGNED` | No | `0.00` | Non-negative per-unit cost |
| `inventory_status` | ENUM | No | `AVAILABLE` | `AVAILABLE`, `LOW_STOCK`, `OUT_OF_STOCK`, `BLOCKED`, `INACTIVE` |
| `last_updated` | `TIMESTAMP` | No | Current/update timestamp | Last persistent change |

Constraint: `UNIQUE (lab_id, component_id, storage_location_id)`. The referenced STORAGE_LOCATION must belong to the same LAB as the INVENTORY row; enforce through service validation and, only if approved in Phase 2, a narrow invariant trigger. No quantity may be negative.

### 4.9 COMPONENT_REQUEST

| Attribute | Type baseline | Null | Key/default | Rule |
|---|---|---:|---|---|
| `request_id` | `BIGINT UNSIGNED` | No | PK, AUTO_INCREMENT | Request header identifier |
| `requesting_lab_id` | `BIGINT UNSIGNED` | No | FK → LAB | Destination/requesting lab |
| `created_by` | `BIGINT UNSIGNED` | No | FK → USER | Request creator |
| `request_date` | `DATE` | No | — | Creation/business date |
| `required_by_date` | `DATE` | No | — | Must be on/after request date |
| `priority` | ENUM | No | `MEDIUM` | `LOW`, `MEDIUM`, `HIGH`, `URGENT` |
| `reason` | `VARCHAR(1000)` | No | — | Academic/operational reason |
| `request_status` | ENUM | No | `DRAFT` | `DRAFT`, `SUBMITTED`, `PARTIALLY_APPROVED`, `APPROVED`, `FULFILLED`, `REJECTED`, `CANCELLED` |

Constraint: `CHECK (required_by_date >= request_date)`. A request must contain at least one REQUEST_ITEM before submission.

### 4.10 REQUEST_ITEM

| Attribute | Type baseline | Null | Key/default | Rule |
|---|---|---:|---|---|
| `request_item_id` | `BIGINT UNSIGNED` | No | PK, AUTO_INCREMENT | Request-line identifier |
| `request_id` | `BIGINT UNSIGNED` | No | FK → COMPONENT_REQUEST | Owning request |
| `component_id` | `BIGINT UNSIGNED` | No | FK → COMPONENT | Requested component |
| `quantity_requested` | `INT UNSIGNED` | No | — | Must be greater than zero |
| `quantity_approved` | `INT UNSIGNED` | No | `0` | Between zero and requested quantity |
| `item_status` | ENUM | No | `PENDING` | `PENDING`, `PARTIALLY_APPROVED`, `APPROVED`, `REJECTED`, `ALLOCATED`, `FULFILLED` |
| `remarks` | `VARCHAR(500)` | Yes | — | Review/allocation note |

Constraints: `UNIQUE (request_id, component_id)` and `CHECK (quantity_requested > 0 AND quantity_approved <= quantity_requested)`.

### 4.11 TRANSFER

| Attribute | Type baseline | Null | Key/default | Rule |
|---|---|---:|---|---|
| `transfer_id` | `BIGINT UNSIGNED` | No | PK, AUTO_INCREMENT | Transfer header identifier |
| `request_id` | `BIGINT UNSIGNED` | No | FK → COMPONENT_REQUEST | Every transfer fulfils one request |
| `source_lab_id` | `BIGINT UNSIGNED` | No | FK → LAB | Sending lab |
| `destination_lab_id` | `BIGINT UNSIGNED` | No | FK → LAB | Receiving/requesting lab |
| `created_by` | `BIGINT UNSIGNED` | No | FK → USER | Transfer creator/submitting user |
| `received_by` | `BIGINT UNSIGNED` | Yes | FK → USER | NULL until receipt confirmation |
| `dispatch_date` | `DATE` | Yes | — | NULL before dispatch |
| `received_date` | `DATE` | Yes | — | NULL before receipt; not before dispatch |
| `transfer_status` | ENUM | No | `DRAFT` | `DRAFT`, `APPROVED`, `DISPATCHED`, `RECEIVED`, `PARTIALLY_RETURNED`, `RETURNED`, `CANCELLED` |
| `approval_status` | ENUM | No | `PENDING` | `PENDING`, `APPROVED`, `REJECTED` |

Constraints: source and destination labs must differ; received date cannot precede dispatch; receipt identity/date remain NULL until receipt. A transfer must contain at least one TRANSFER_ITEM before approval or dispatch.

### 4.12 TRANSFER_ITEM

| Attribute | Type baseline | Null | Key/default | Rule |
|---|---|---:|---|---|
| `transfer_item_id` | `BIGINT UNSIGNED` | No | PK, AUTO_INCREMENT | Transfer-line identifier |
| `transfer_id` | `BIGINT UNSIGNED` | No | FK → TRANSFER | Owning transfer |
| `inventory_id` | `BIGINT UNSIGNED` | No | FK → INVENTORY | Original/source inventory allocation |
| `quantity_sent` | `INT UNSIGNED` | No | — | Greater than zero |
| `quantity_received` | `INT UNSIGNED` | No | `0` | Between zero and sent quantity |
| `return_due_date` | `DATE` | Yes | — | Non-NULL marks temporary sharing |
| `return_date` | `DATE` | Yes | — | Actual temporary return date |
| `condition_on_issue` | `VARCHAR(100)` | Yes | — | Recorded at dispatch |
| `condition_on_return` | `VARCHAR(100)` | Yes | — | Recorded only on actual return |

Constraints: `UNIQUE (transfer_id, inventory_id)` and `CHECK (quantity_sent > 0 AND quantity_received <= quantity_sent)`. `inventory_id` is the source inventory only; there is no destination-inventory FK.

### 4.13 DISPOSAL_RECORD

| Attribute | Type baseline | Null | Key/default | Rule |
|---|---|---:|---|---|
| `disposal_id` | `BIGINT UNSIGNED` | No | PK, AUTO_INCREMENT | Disposal event identifier |
| `inventory_id` | `BIGINT UNSIGNED` | No | FK → INVENTORY | Affected stock row |
| `authorized_by` | `BIGINT UNSIGNED` | No | FK → USER | Administrator authorizer |
| `quantity_disposed` | `INT UNSIGNED` | No | — | Greater than zero and not above available stock |
| `disposal_date` | `DATE` | No | — | Event date |
| `disposal_reason` | `VARCHAR(500)` | No | — | Reason for lifecycle removal |
| `disposal_method` | `VARCHAR(120)` | No | — | Approved disposal method |
| `remarks` | `VARCHAR(500)` | Yes | — | Optional explanatory note |

Constraint: `CHECK (quantity_disposed > 0)`. Full stock validation and decrement occur inside a row-locked transaction.

## 5. Foreign-key and referential-action policy

| Child FK | Parent | Delete policy | Reason |
|---|---|---|---|
| LAB_CONTACT.`lab_id` | LAB | CASCADE | Owned multivalued attribute |
| USER.`lab_id` | LAB | RESTRICT | Preserve user/master references |
| USER_PHONE.`user_id` | USER | CASCADE | Owned multivalued attribute |
| COMPONENT.`category_id` | COMPONENT_CATEGORY | RESTRICT | Preserve catalogue classification |
| STORAGE_LOCATION.`lab_id` | LAB | RESTRICT | Preserve physical/location history |
| INVENTORY lab/component/location FKs | LAB / COMPONENT / STORAGE_LOCATION | RESTRICT | Preserve stock integrity |
| COMPONENT_REQUEST lab/creator FKs | LAB / USER | RESTRICT | Preserve request history |
| REQUEST_ITEM.`request_id` | COMPONENT_REQUEST | CASCADE only for controlled pre-operational header deletion; otherwise status/history policy | Owned request lines |
| REQUEST_ITEM.`component_id` | COMPONENT | RESTRICT | Preserve request meaning |
| TRANSFER request/lab/user FKs | COMPONENT_REQUEST / LAB / USER | RESTRICT | Preserve transfer lifecycle |
| TRANSFER_ITEM.`transfer_id` | TRANSFER | CASCADE only for controlled pre-operational deletion; otherwise history policy | Owned transfer lines |
| TRANSFER_ITEM.`inventory_id` | INVENTORY | RESTRICT | Preserve allocation history |
| DISPOSAL_RECORD inventory/user FKs | INVENTORY / USER | RESTRICT | Preserve disposal history |

Use `ON UPDATE CASCADE` consistently on identifier FKs. The service layer must prevent deletion of submitted/approved/operational headers even where an owned-line cascade exists. Operational history is preserved through status transitions, not casual hard deletion.

## 6. Validated relationship, cardinality and participation matrix

| Relationship sentence | Cardinality | Parent participation | Child/relationship participation | Relational implementation |
|---|---:|---|---|---|
| LAB employs USER | 1:N | LAB 1..N in conceptual operating model | USER exactly 1 | USER.`lab_id` |
| LAB contains STORAGE_LOCATION | 1:N | LAB 1..N conceptually | Location exactly 1 | STORAGE_LOCATION.`lab_id` |
| COMPONENT_CATEGORY classifies COMPONENT | 1:N | Category 0..N | Component exactly 1 | COMPONENT.`category_id` |
| COMPONENT appears in INVENTORY | 1:N | Component 0..N | Inventory exactly 1 | INVENTORY.`component_id` |
| STORAGE_LOCATION stores INVENTORY | 1:N | Location 0..N | Inventory exactly 1 | INVENTORY.`storage_location_id` |
| LAB maintains INVENTORY | 1:N | Lab 0..N | Inventory exactly 1 | INVENTORY.`lab_id` |
| LAB raises COMPONENT_REQUEST | 1:N | Lab 0..N | Request exactly 1 | COMPONENT_REQUEST.`requesting_lab_id` |
| USER creates COMPONENT_REQUEST | 1:N | User 0..N | Request exactly 1 | COMPONENT_REQUEST.`created_by` |
| COMPONENT_REQUEST includes REQUEST_ITEM | 1:N | Submitted request 1..N | Item exactly 1 | REQUEST_ITEM.`request_id` |
| COMPONENT is requested as REQUEST_ITEM | 1:N | Component 0..N | Item exactly 1 | REQUEST_ITEM.`component_id` |
| USER submits TRANSFER | 1:N | User 0..N | Transfer exactly 1 | TRANSFER.`created_by` |
| USER receives TRANSFER | 1:N | User 0..N | Transfer 0..1 until receipt | TRANSFER.`received_by` nullable |
| LAB sends TRANSFER | 1:N | Lab 0..N | Transfer exactly 1 | TRANSFER.`source_lab_id` |
| LAB receives TRANSFER | 1:N | Lab 0..N | Transfer exactly 1 | TRANSFER.`destination_lab_id` |
| COMPONENT_REQUEST is fulfilled by TRANSFER | 1:N | Request 0..N | Transfer exactly 1 | TRANSFER.`request_id` |
| TRANSFER contains TRANSFER_ITEM | 1:N | Approved/operational transfer 1..N | Item exactly 1 | TRANSFER_ITEM.`transfer_id` |
| INVENTORY is allocated to TRANSFER_ITEM | 1:N | Inventory 0..N over time | Item exactly 1 | TRANSFER_ITEM.`inventory_id` |
| INVENTORY is disposed through DISPOSAL_RECORD | 1:N | Inventory 0..N | Disposal exactly 1 | DISPOSAL_RECORD.`inventory_id` |
| USER authorizes DISPOSAL_RECORD | 1:N | User 0..N | Disposal exactly 1 | DISPOSAL_RECORD.`authorized_by` |

No direct TRANSFER → DISPOSAL_RECORD relationship exists. No forced 1:1, weak entity, specialization/generalization, overlap/disjoint, union/category or aggregation construct is added.

## 7. Associative entities and normalization position

- REQUEST_ITEM resolves the conceptual M:N between COMPONENT_REQUEST and COMPONENT.
- TRANSFER_ITEM resolves the conceptual M:N between TRANSFER and INVENTORY.
- INVENTORY represents the operational COMPONENT ↔ STORAGE_LOCATION association while also recording LAB ownership.
- LAB_CONTACT and USER_PHONE implement multivalued attributes in 1NF.

The schema targets at least 3NF. Candidate keys and functional dependencies must be evaluated relation-by-relation before claiming BCNF. Descriptive lab/category/component/location data remains in its master relation; transactional rows store FKs rather than copied descriptions.

## 8. Role-based permissions

| Role | Permitted operations | Restrictions |
|---|---|---|
| STUDENT | View catalogue and availability; create, submit and view own-lab requests | No master edits, inventory changes, approvals, transfer execution or disposal |
| FACULTY | View relevant data; create requests; review/approve quantities for assigned lab; monitor transfer progress | No global configuration or disposal unless separately Administrator |
| LAB_ASSISTANT | Manage assigned-lab storage/inventory; prepare allocations; dispatch, receive and return transfers; record quantities/conditions | No global master control; no disposal authorization |
| ADMINISTRATOR | Full master/user administration; all-lab visibility; disposal authorization; controlled corrections | Still bound by status rules, confirmations, transactions and history preservation |

Authorization is enforced in both UI navigation and service functions. Lab-scoped roles may access only their assigned lab except for the opposite side of a valid transfer. INACTIVE or SUSPENDED users cannot perform operational writes.

## 9. Authentication decision

The frozen USER relation does not contain `password_hash`.

Authentication flow:

1. Verify an externally stored hashed demonstration credential in protected Streamlit secrets/local configuration.
2. Map the authenticated email to USER.`email`.
3. Load USER.`role`, USER.`lab_id` and USER.`account_status`.
4. Reject missing, INACTIVE or SUSPENDED users.
5. Establish session identity and re-check role/lab scope in every service method.

Never store plaintext passwords, commit real secrets, log credential material or run the application as MySQL root.

## 10. Request workflow and states

### 10.1 Workflow

1. Authorized user creates a DRAFT request header for the assigned/requesting lab.
2. User adds one or more unique component lines with positive quantities.
3. Submission validates dates, creator/lab scope and at least one line.
4. Faculty/Administrator reviews each line and assigns approved quantity/status.
5. Service recomputes the header from item outcomes in the same transaction.
6. Approved quantities may be fulfilled by one or more TRANSFER records.
7. Header becomes FULFILLED only when all non-rejected approved quantities are fulfilled.

### 10.2 Request state transitions

| From | Allowed next state | Trigger/rule |
|---|---|---|
| DRAFT | SUBMITTED | At least one valid item |
| DRAFT | CANCELLED | Creator cancels before submission |
| SUBMITTED | PARTIALLY_APPROVED | At least one item partly/fully approved and at least one not fully approved/rejected |
| SUBMITTED | APPROVED | All accepted items fully approved |
| SUBMITTED | REJECTED | All items rejected/zero approved |
| SUBMITTED | CANCELLED | Authorized cancellation before allocation/reservation |
| PARTIALLY_APPROVED | APPROVED | Remaining accepted items finalized as fully approved |
| PARTIALLY_APPROVED | FULFILLED | All approved quantity fulfilled; rejected/unapproved quantity does not count |
| APPROVED | FULFILLED | All approved quantity fulfilled |

Backward transitions are rejected. Header status is derived/maintained from item and fulfilment state, never manually contradicted.

### 10.3 Request-item transitions

`PENDING → PARTIALLY_APPROVED | APPROVED | REJECTED → ALLOCATED → FULFILLED`.

PARTIALLY_APPROVED and APPROVED items may move to ALLOCATED for their approved quantities. An item becomes FULFILLED only when its approved quantity is received/accepted according to transfer progress.

## 11. Frozen inventory quantity semantics

`quantity_available` means physical stock currently free for a new allocation.

`quantity_reserved` means stock reserved for an approved transfer but not yet dispatched.

For any inventory row, both values are non-negative. All transitions below use an explicit transaction, server-side authorization/validation and `SELECT ... FOR UPDATE` when stock can change concurrently.

| Event | `quantity_available` | `quantity_reserved` | Rule |
|---|---:|---:|---|
| Before reservation | Existing free quantity | Existing reserved quantity | Example: 100 / 0 |
| Transfer approval/reservation of Q | `available - Q` | `reserved + Q` | Reject if Q exceeds pre-reservation available stock |
| Cancellation/rejection before dispatch | `available + released` | `reserved - released` | Release only the affected reservation |
| Dispatch of quantity_sent | No second subtraction | `reserved - quantity_sent` | Stock already left free availability at approval |
| Receipt | Destination `available + quantity_received` | Destination unchanged | Select/create valid destination row |
| Temporary return | Destination `available - returned`; source `available + returned` | Unchanged | Validate both rows and record return |
| Disposal | `available - disposed` | Unchanged | Reject if disposal exceeds free available stock |

Stable inventory row-lock ordering is mandatory when multiple rows are modified. Dispatch must never subtract `quantity_available` a second time.

## 12. Transfer workflow, destination limitation and states

### 12.1 Planning

1. Choose an approved/partially approved request.
2. Use distinct source and destination labs; destination normally equals the requesting lab.
3. Add at least one unique source INVENTORY allocation through TRANSFER_ITEM.
4. Validate that allocated components correspond to approved request items and that source inventory belongs to source lab.

### 12.2 Approval/reservation

1. Lock all source inventory rows in stable order.
2. Re-check authorization, request state and free availability.
3. Move each approved quantity from available to reserved.
4. Set approval_status = APPROVED and transfer_status = APPROVED.
5. Commit all lines and header together; otherwise roll back.

Rejection sets approval_status = REJECTED and transfer_status = CANCELLED without reserving stock. Cancellation after approval but before dispatch releases the exact reservation and sets CANCELLED.

### 12.3 Dispatch

Require approved state. Lock rows, validate reserved quantities, reduce only `quantity_reserved` by `quantity_sent`, set `dispatch_date`, record `condition_on_issue`, set DISPATCHED and commit atomically.

### 12.4 Receipt

The receiving Lab Assistant explicitly selects an existing destination inventory row or a destination storage location for each received component. The service validates destination lab, component, location ownership and the unique inventory position. It locks the affected rows; increments or creates destination INVENTORY; stores `quantity_received`, `received_by`, `received_date`; and recomputes transfer/request progress atomically.

**Intentional MVP limitation:** TRANSFER_ITEM stores only the original/source `inventory_id`. It does not store a destination-inventory FK. The selected destination inventory/location is therefore validated at receipt/return but is not added as a hidden attribute or relation.

### 12.5 Temporary return

A non-NULL `return_due_date` marks a returnable transfer line. On return, the operator explicitly selects and validates the destination inventory row, locks source and destination rows in stable order, decrements destination available quantity, restores source available quantity, writes `return_date` and `condition_on_return`, and recomputes header state. Receipt condition is not separately persisted.

### 12.6 Transfer state transitions

| Approval/status from | Allowed next state | Rule |
|---|---|---|
| PENDING / DRAFT | APPROVED / APPROVED | Successful row-locked reservation |
| PENDING / DRAFT | REJECTED / CANCELLED | No reservation |
| APPROVED / APPROVED | APPROVED / CANCELLED | Release reservation before dispatch |
| APPROVED / APPROVED | APPROVED / DISPATCHED | Reduce reserved only; stamp dispatch |
| APPROVED / DISPATCHED | APPROVED / RECEIVED | Record receipt and destination stock |
| APPROVED / RECEIVED | APPROVED / PARTIALLY_RETURNED | Some required temporary quantity returned |
| APPROVED / RECEIVED or PARTIALLY_RETURNED | APPROVED / RETURNED | All temporary return obligations complete |

Permanent transfers remain RECEIVED when no return is due. Cancellation after dispatch is not permitted; correction requires a controlled return/reversal workflow, not a backward state change.

## 13. Disposal workflow

1. ADMINISTRATOR selects an inventory row and enters positive quantity, date, reason, method and optional remarks.
2. Service verifies ACTIVE account and Administrator role.
3. Begin transaction and lock the inventory row.
4. Reject quantity above `quantity_available`; reserved stock cannot be disposed.
5. Insert DISPOSAL_RECORD and decrement available quantity.
6. Recompute inventory status if the documented status rule requires it.
7. Commit together or roll back completely.

DISPOSAL_RECORD links to INVENTORY and USER only. It does not link directly to TRANSFER.

## 14. Inventory status and low-stock rule

- `OUT_OF_STOCK`: free available quantity is zero, subject to BLOCKED/INACTIVE precedence.
- `LOW_STOCK`: schema-supported low-stock views compare aggregated available stock with COMPONENT.`minimum_stock_level`.
- `AVAILABLE`: free stock exists and the record is not low, blocked or inactive.
- `BLOCKED` and `INACTIVE`: controlled administrative operational states; they prevent new allocation.

The SQL view/query is the authoritative analytics source for low-stock reporting. If Phase 2 chooses to synchronize the stored `inventory_status`, the rule must be narrow, deterministic, documented and tested; no hidden full workflow belongs in a trigger.

## 15. Transaction and concurrency boundaries

Explicit transactions are mandatory for:

- request review/status recomputation;
- transfer approval/reservation;
- reservation release;
- dispatch;
- receipt and destination inventory creation/increment;
- temporary return;
- disposal.

Rules:

- use row locks on mutable stock rows;
- lock multiple rows in ascending `inventory_id` order;
- re-check quantities after locks are acquired;
- update header/line/item states within the same unit of work;
- commit only after all validations and writes succeed;
- roll back on every exception;
- translate integrity/concurrency failures into user-friendly messages;
- never fabricate a successful workflow after rollback.

## 16. Validation, security and integrity rules

- Parameterized SQL/SQLAlchemy binding only; no user-input SQL concatenation.
- Every FK indexed; add justified status/date/search indexes in Phase 2.
- Validate dates, domains, required fields, positive quantities and cross-table lab ownership server-side.
- Prevent negative available/reserved quantities and over-approval/over-receipt/over-disposal.
- Restrict cross-lab writes according to RBAC and valid transfer roles.
- Use least-privilege MySQL application account; do not require root.
- Keep secrets in environment/Streamlit secrets; commit only templates with fake values.
- Log technical exceptions to rotating local logs without credentials or sensitive values.
- Use confirmation for dispatch, receipt, return, disposal and destructive master-data operations.
- Preserve lifecycle history; prefer state changes over hard deletion.

## 17. MVP modules

- Authentication adapter and session management.
- RBAC and laboratory scope.
- Laboratory, lab contact, user and user-phone administration.
- Component category and component catalogue.
- Storage locations.
- Inventory availability, reservation, valuation and minimum-stock analytics.
- Multi-line component requests and approvals.
- Transfer planning, approval, reservation, dispatch and receipt.
- Temporary return tracking.
- Authorized disposal.
- Dashboard, filters, SQL-backed analytics and mandatory CSV export.
- Tests, documentation, demonstration and viva preparation.

## 18. Future-scope exclusions

The following are not implemented in MVP and may not introduce core tables or active modules without a versioned approval:

- procurement, vendors, purchase orders and GRN;
- maintenance, calibration and repair;
- serialized asset instances;
- individual borrowing and penalties;
- dedicated QR_TAG architecture;
- compatibility/substitute mapping;
- audit-log database table;
- AI forecasting, predictive maintenance and image recognition;
- IoT smart cabinets;
- inter-college sharing;
- enterprise ERP functions and microservices.

CSV export is mandatory. Printable PDF/ReportLab output is optional enhancement only.

## 19. Technology stack and architecture

| Area | Frozen choice |
|---|---|
| Database | MySQL Community Server 8.4.11 LTS, InnoDB, utf8mb4 |
| Language | Python 3.12+ |
| Frontend | Streamlit |
| Data access | SQLAlchemy 2.x with PyMySQL |
| Analytics | SQL views/aggregations, pandas, Plotly |
| Configuration | python-dotenv and/or Streamlit secrets |
| Authentication | bcrypt or passlib hashes stored outside core schema |
| Testing | pytest, unit and dedicated integration database tests |
| Logging | Python logging with safe rotating file handler |
| Optional output | ReportLab only if printable PDF is later approved |

Architecture:

`Streamlit pages → service/business layer → repository/data-access layer → SQLAlchemy/MySQL`

Pages contain no raw SQL. Repositories contain persistence/query code but no authorization or workflow decisions. Services own RBAC, states, cross-table validation and transactions. Reports are read-only.

## 20. Naming conventions

- Conceptual/document names: uppercase relation names.
- MySQL objects/columns: lowercase `snake_case`.
- Full-project database: `sems_db`.
- Quote raw SQL table name `` `user` ``.
- Python modules/functions/variables: lowercase `snake_case`; classes: `PascalCase`; constants: uppercase `SNAKE_CASE`.
- Foreign keys use the parent identifier name (`lab_id`, `component_id`, etc.) with role prefixes where necessary (`source_lab_id`, `destination_lab_id`).
- Full-project manufacturer column is `manufacturer_details`; Assignment 2/3 `manufacturer_info` remains only in the coursework mapping.
- Status constants use the exact uppercase values frozen in this register.

## 21. Assignment 2/3 boundary

The teaching schema `laboratory`, `component_category`, `electronic_component`, `storage_location`, `inventory` and database name `smart_electronics_lab_ddl` may be used to demonstrate earlier DDL/DML continuity and reuse verified example values. It is not the complete SEMS schema, does not govern full-project naming, and cannot replace the 13 relations.

## 22. Phase gates and implementation order

| Phase | Scope | State after this freeze |
|---:|---|---|
| 0 | Source ingestion and initialization audit | Verified complete |
| 1 | Requirements/schema freeze and checkpoint controls | Verified complete |
| 2 | DDL, constraints, indexes, views, seed data, routines/triggers | Ready; requires approval |
| 3 | Connectivity and repositories | Pending |
| 4 | Authentication and RBAC | Pending |
| 5 | Master-data screens | Pending |
| 6 | Inventory | Pending |
| 7 | Requests | Pending |
| 8 | Transfers | Pending |
| 9 | Disposal | Pending |
| 10 | Analytics/dashboard | Pending |
| 11 | Automated/manual testing | Pending |
| 12 | Documentation alignment | Pending |
| 13 | GitHub, demonstration and viva preparation | Pending |
| 14 | Final audit and packaging | Pending |

## 23. Change-control policy

Any proposed change affecting a frozen relation, attribute, datatype, PK, FK, unique/check/domain rule, nullability, status, cardinality, participation, transaction rule or MVP boundary must:

1. be raised before implementation;
2. receive a unique decision ID;
3. explain academic and operational impact;
4. identify affected SQL, Python, UI, tests and documentation;
5. specify migration/backward-compatibility consequences;
6. receive explicit user approval;
7. increment the baseline version;
8. update DECISION_LOG, CHANGELOG, PROJECT_STATE and ARTIFACT_MANIFEST.

Bug fixes that preserve this semantics do not require a schema-version increment but must still be logged.

## 24. Phase 1 acceptance statement

The current recovery directive is the explicit authority to freeze this baseline. Phase 1 is complete when the DOCX register and checkpoint files are present and validated.

**Formal freeze marker:**

> **SEMS BASELINE v1.0 — FROZEN FOR IMPLEMENTATION**

**Implementation resumption statement:** Implementation will resume from Phase 2 because Phases 0–1 have been verified complete. Phase 2 Database Foundation must not begin until the user explicitly approves it.

## 25. No-fabrication statement

This register freezes requirements only. It does not claim that SQL was generated or executed, MySQL accepted the schema, the Streamlit application exists, tests passed, screenshots were captured, Git was configured or deployment occurred.
