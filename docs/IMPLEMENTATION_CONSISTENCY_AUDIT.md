# SEMS Implementation Consistency Audit

**Audit date:** 2026-08-22  
**Authority:** SEMS Baseline v1.0 and current maximum-quality directive  
**Boundary:** exactly 13 base relations; no schema redesign

## Audit method

The audit traced each frozen relation through `sql/01_schema.sql`, SQLAlchemy mappings, repositories, services, Streamlit pages, tests and documentation. It compared names, columns, MySQL types, nullability, defaults, PK/FK/UNIQUE/CHECK rules, state domains, referential actions and operational participation. It also reviewed the nine numbered/support SQL scripts, three optional demo scripts and every stock-changing transaction.

Actual MySQL execution was unavailable in this environment. Results below are static/source-level findings unless explicitly identified otherwise.

## Frozen relation trace

| Relation | Responsibility | PK | Main FKs / integrity | Application path |
|---|---|---|---|---|
| `lab` | Laboratory master | `lab_id` | UNIQUE `(lab_name, department_name)` | lab repository → master-data service → Laboratories |
| `lab_contact` | Normalized multivalued lab contacts | `(lab_id, contact_number)` | `lab_id → lab`, CASCADE delete | lab repository → master-data service → Laboratories |
| ``user`` | User identity, role, account state and lab assignment | `user_id` | `lab_id → lab`; UNIQUE email; reserved name always quoted | user repository → auth/master services → Users/login |
| `user_phone` | Normalized multivalued user phones | `(user_id, phone_number)` | `user_id → user`, CASCADE delete | user repository → master-data service → Users |
| `component_category` | Component classification master | `category_id` | UNIQUE category name | component repository → master-data service → Catalogue |
| `component` | Reusable electronic-component definition | `component_id` | `category_id → component_category`; nullable UNIQUE part number; nonnegative minimum | component repository → master-data service → Catalogue |
| `storage_location` | Lab-owned cabinet/shelf/drawer position | `storage_location_id` | `lab_id → lab`; nullable-coordinate UNIQUE plus service normalization | lab repository → master-data service → Storage Locations |
| `inventory` | Lab/component/location stock association | `inventory_id` | three FKs; UNIQUE position; nonnegative stock/cost; same-lab triggers | inventory repository → inventory/transfer/disposal services → Inventory |
| `component_request` | Request header and creator/lab/date/state | `request_id` | lab/creator FKs; date CHECK | request repository → request service → Component Requests |
| `request_item` | Associative request line with requested/approved quantities | `request_item_id` | request/component FKs; UNIQUE line; quantity CHECKs | request repository → request/transfer services → Component Requests |
| `transfer` | Request-linked source/destination lifecycle header | `transfer_id` | request, two lab and two user-role FKs; state/date/receipt CHECKs | transfer repository → transfer service → Transfers |
| `transfer_item` | Associative source-inventory allocation | `transfer_item_id` | transfer/source-inventory FKs; UNIQUE allocation; sent/received/return CHECKs | transfer repository → transfer service → Transfers |
| `disposal_record` | Immutable operational disposal event | `disposal_id` | inventory/authorizer FKs; positive quantity | disposal repository → disposal service → Disposal |

## Type/default/referential alignment

- Surrogate IDs and their FKs are consistently `BIGINT UNSIGNED`; stock/minimum fields are `INT UNSIGNED`; cost is `DECIMAL(12,2) UNSIGNED`.
- Dates use `DATE`; only `inventory.last_updated` uses `TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP`.
- SQL and ORM defaults agree for account, inventory, request and transfer states and numeric zero defaults.
- Parent master/history references use `ON DELETE RESTRICT`; owned multivalued/line rows use the frozen CASCADE rules.
- SQLAlchemy maps ``user`` with a forced quoted name. Raw SQL consistently uses backticks; no unquoted persistence reference was detected.
- Exactly seven reporting views, one function, one procedure and two narrow same-lab inventory triggers are present. They add no base relation.

## Material findings and resolutions

| Severity | Finding | Resolution implemented | Schema effect |
|---|---|---|---|
| MAJOR | Faculty could approve/reject/cancel transfers, conflicting with the frozen Administrator approval decision | Approval/rejection is Administrator-only; cancellation is Lab Assistant/Administrator; Faculty retains monitoring | None |
| MAJOR | Student could inspect lab-wide transfer detail and operational reports beyond own-request scope | Transfer page/service denied to Student; report allowlist added; request-progress report/dashboard scoped by `created_by` | None |
| MAJOR | Dashboard “inventory valuation” counted only available stock, while the authoritative formula includes reserved stock still on hand | Added `inventory_value = (available + reserved) × unit_cost`; dashboard and verification use it; `available_value` remains explicitly available-only | View/query only |
| MAJOR | A database role/lab/status change did not immediately invalidate an existing Streamlit session | Every active UI session and actor-aware service now revalidates USER email, role, lab and ACTIVE state | None |
| MAJOR | Frozen request transitions allowed SUBMITTED cancellation before approval, but implementation exposed DRAFT-only cancellation | Added creator/Admin cancellation for DRAFT or SUBMITTED, with lab scope and backward-transition rejection | None |
| MAJOR | Multiple receipt lines creating the same destination component/location could collide inside one transaction | New destination positions are reused by `(lab, component, location)` within the receipt transaction; concurrent UNIQUE conflicts roll back safely | None |
| MINOR | Approval quantities could be revised after a transfer allocation began | Request review now rejects revision after allocated/fulfilled state or nonzero transfer allocation | None |
| MINOR | Formula-like exported text could execute when CSV is opened in spreadsheet software | Text beginning (after leading whitespace) with `=`, `+`, `-` or `@` is prefixed with an apostrophe | None |
| MINOR | Configuration errors and invalid numeric settings were not always consolidated safely | Startup/preflight validation, placeholder detection and connection timeout were added; no credential value is printed | None |
| MINOR | Several IDs, strings, dates, phone/email values and text lengths relied too heavily on widgets/DB errors | Central service validators and user-safe errors were added; nullable storage coordinates remain null-normalized | None |
| INFORMATIONAL | Partial receipt has no separate header state | Transfer remains DISPATCHED until all lines are fully received, exactly because no `PARTIALLY_RECEIVED` state exists | Frozen limitation |
| INFORMATIONAL | Destination inventory is not persisted on TRANSFER_ITEM | Explicit destination selection/validation remains runtime-only; no hidden FK was introduced | Frozen limitation |

## Architecture and transaction result

- Streamlit pages contain no repository imports, SQL execution or transaction ownership.
- Repositories contain persistence/query logic but no role decisions or state transitions.
- Services own validation, RBAC, workflow changes and transactions.
- Reservation, cancellation, dispatch, receipt, whole-line temporary return and disposal use one `session_scope()` transaction.
- Multi-row stock locks use the repository helper that sorts unique `inventory_id` values before `SELECT ... FOR UPDATE`.
- Request headers/lines are locked during review; request headers are also locked when transfer allocation starts, preventing approval/allocation races.
- Every exception leaves commit control to `session_scope()`, which rolls back and closes the session.

## Audit conclusion

The implementation remains faithful to Baseline v1.0 and exactly 13 base relations. All justified source-level CRITICAL/MAJOR consistency findings were corrected without adding attributes, FKs, tables or future-scope modules. Runtime MySQL 8.4.11 syntax/behavior and Workbench inspection remain pending local acceptance.
