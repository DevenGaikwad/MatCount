# SEMS Query Optimization Report

**Target:** MySQL Community Server 8.4.11 LTS / InnoDB  
**Evidence script:** `academic_demo/sql/05_views_indexes_explain.sql`  
**Current evidence state:** static SQL reviewed; fresh local optimizer output must be captured because plans depend on real data distribution and statistics.

## Optimization method

SEMS uses a measured sequence:

1. identify frequent filters, joins, ordering and row-lock lookups;
2. reuse PK, UNIQUE and FK indexes before adding secondary indexes;
3. place equality/filter columns before range/order columns in composite indexes;
4. bound interactive results with `LIMIT` and page in the UI;
5. inspect `EXPLAIN`, then use read-only bounded `EXPLAIN ANALYZE` when safe;
6. remove an index if fresh plan/use evidence does not justify its write/storage cost.

`EXPLAIN ANALYZE` executes the query, so the bundled example is a read-only `SELECT`. Never apply it casually to a mutating statement.

## Existing key access paths

Primary, UNIQUE and FK indexes are part of `sql/01_schema.sql`. Important natural access paths include:

- `inventory(lab_id, component_id, storage_location_id)` UNIQUE for position identity and lab/component lookup;
- `request_item(request_id, component_id)` UNIQUE for one component per request;
- `transfer_item(transfer_id, inventory_id)` UNIQUE for one source position per transfer;
- `component.email` does not exist; `user(email)` UNIQUE supports authentication identity lookup;
- all surrogate PKs support stable detail lookup and ordered row locking.

The sentence above intentionally distinguishes entities: authentication uses ``user(email)``, never COMPONENT.

## Justified secondary indexes

| Index | Leading access pattern | Representative use | Why it is not redundant |
|---|---|---|---|
| `idx_component_name(component_name)` | name prefix/order | catalogue search `LIKE 'R%'` | UNIQUE part number cannot serve name search |
| `idx_component_category_name(category_id, component_name)` | category equality + name order | category catalogue | leading category differs from name-only search |
| `idx_user_lab_role_status(lab_id, role, account_status)` | lab + role/status | scoped active-user administration | email UNIQUE serves a different lookup |
| `idx_inventory_component_status(component_id, inventory_status)` | component + stock state | availability allocation candidates | position UNIQUE leads with lab |
| `idx_inventory_status_updated(inventory_status, last_updated)` | state + recent update | operational stock queue | supports status-first monitoring |
| `idx_request_status_date(request_status, request_date)` | workflow state + time | global review queue | global query has no lab predicate |
| `idx_request_lab_status_required(requesting_lab_id, request_status, required_by_date)` | lab + state + due order | faculty/lab request queue | covers scoped queue distinct from global queue |
| `idx_request_item_status(item_status, component_id)` | line state + component | progress/fulfilment analysis | association UNIQUE leads with request |
| `idx_transfer_status_dates(transfer_status, dispatch_date, received_date)` | state + event date | global lifecycle queue | date order/filter not covered by PK/FKs |
| `idx_transfer_approval_status(approval_status, transfer_status)` | approval + lifecycle | administrator approval queue | approval is not the leading field elsewhere |
| `idx_transfer_source_status(source_lab_id, transfer_status)` | source lab + state | dispatch queue | source FK alone does not cover state |
| `idx_transfer_destination_status(destination_lab_id, transfer_status)` | destination lab + state | receipt queue | destination is a separate relationship role |
| `idx_transfer_item_overdue(return_due_date, return_date, transfer_id)` | due-date range + completion | overdue-return view | natural association key leads with transfer |
| `idx_disposal_date_inventory(disposal_date, inventory_id)` | date range + position | disposal timeline | inventory FK alone does not support date-first reports |

Indexes are deliberately not added on every status/quantity column. Low-selectivity ENUM indexes are useful here only when combined with scope/date columns or used for small operational subsets. Quantity arithmetic is calculated from base rows/views rather than indexed without measured need.

## Representative plan demonstrations

| Query | Expected access reasoning | Faculty action |
|---|---|---|
| Component prefix availability | `idx_component_name` can provide a selective range; `LIKE '%text%'` cannot use the prefix efficiently | compare the first two plans in `05_views_indexes_explain.sql` |
| Own-lab request queue | equality on lab, range/list on status, ordering by required date aligns with `idx_request_lab_status_required` | inspect chosen key, estimated/actual rows and sort operation |
| Source-lab transfer queue | source lab + transfer state aligns with `idx_transfer_source_status` | verify chosen key and rows examined |
| Low-stock view | view expands to joins/aggregation; lab restriction should be pushed where possible | inspect tree and explain view abstraction trade-off |
| Component/status inventory | `idx_inventory_component_status` matches both predicates; bounded `EXPLAIN ANALYZE` reports actual iterator timings | compare estimated vs actual rows |

## Before/after evidence protocol

On the local demonstration database:

1. run `ANALYZE TABLE` only if permitted and statistics are stale;
2. execute `EXPLAIN FORMAT=TREE` for the query with the production index present;
3. record chosen index, estimated rows, access type, sorting/temp-table notes;
4. do **not** drop production indexes for a screenshot;
5. if a before-without-index comparison is academically required, reproduce the relevant table/data in `sems_academic_demo`, omit only that index there, and compare plans safely;
6. execute the bounded read-only `EXPLAIN ANALYZE` and record actual loops/rows/time;
7. explain that a small seed dataset may make a table scan rational—the optimizer is cost-based, not obligated to use an index.

| Evidence item | Fresh local result |
|---|---|
| Server version | PENDING Windows/MySQL run |
| Dataset row counts | PENDING |
| Prefix vs leading-wildcard plans | PENDING |
| Request queue chosen key | PENDING |
| Transfer queue chosen key | PENDING |
| Inventory estimated vs actual rows | PENDING |

No plan or timing is fabricated in this source release.

## Repository-level performance controls

- SQLAlchemy issues parameterized set-oriented statements; list pages do not query each row individually.
- related report facts are joined/aggregated in SQL views instead of N+1 browser requests.
- `get_inventory_rows_for_update()` deduplicates and sorts IDs, then locks all relevant rows in one query.
- API report/inventory limits are bounded to prevent accidental unbounded browser payloads.
- Data tables page locally and allow users to narrow results; production APIs cap report rows.
- dashboard aggregates are consolidated into a bounded set of SQL statements rather than one request per card.
- dynamic report object names are selected from a seven-view allowlist; values remain bound parameters.

The generic report repository uses `SELECT *` only against an allowlisted, documented view surface whose purpose is full report export. Performance-critical operational/detail queries use explicit columns in the SQL demonstrations and ORM models. A future production-scale deployment should measure narrower view projections per role rather than add speculative complexity now.

## Selectivity and maintenance cautions

- A Boolean/ENUM column by itself often has low selectivity; column order must match the real predicate.
- Too many indexes increase INSERT/UPDATE cost, buffer pressure and maintenance.
- an index matching one column may still be rejected for a small table or broad result set.
- stale statistics and skew can change the plan; demonstrate actual data, not memorized output.
- leading-wildcard catalogue search is intentionally shown as a contrast; full-text search is not justified for this MVP.

## Viva explanation

> An index is justified by an access pattern, not by index count. SEMS reuses keys first, then adds composite indexes for catalogue, request, transfer, overdue and disposal queues. I verify them with EXPLAIN and safe EXPLAIN ANALYZE. I also expect the optimizer to choose a scan for a tiny seed dataset, because MySQL is cost-based.

## Primary references

- [MySQL 8.4 EXPLAIN statement](https://dev.mysql.com/doc/refman/8.4/en/explain.html)
- [MySQL 8.4 multiple-column indexes](https://dev.mysql.com/doc/refman/8.4/en/multiple-column-indexes.html)
- [MySQL 8.4 InnoDB transaction model](https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-model.html)

