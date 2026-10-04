# SEMS DBMS Feature Traceability

Use this as the immediate answer to “Where have you demonstrated this DBMS concept?”

| DBMS concept | SEMS evidence | Faculty demonstration |
|---|---|---|
| DDL | `sql/00_database_setup.sql`, `01_schema.sql`, `02_indexes.sql`, `03_views.sql`, `04_routines.sql`, `05_triggers.sql` | Open scripts and expand Workbench schema objects |
| DML | Coherent INSERT seed in `06_seed_data.sql`; transactional service INSERT/UPDATE operations | Show seed rows; perform one Next.js/FastAPI write and confirm with SELECT |
| Primary key | Named `pk_...` constraints on all 13 relations; composite PKs on LAB_CONTACT/USER_PHONE | Workbench table → Indexes; verification query 4 |
| Foreign key | 21 frozen FKs including two LAB and two USER roles on TRANSFER | Workbench table → Foreign Keys; verification query 4 |
| UNIQUE | Lab name/department, email, category name, part number, location/stock/request/transfer line pairs | Run one expected UNIQUE failure in `demo/01` |
| NOT NULL | Required identifiers, names, quantities, states and lifecycle facts | `DESCRIBE inventory` or `DESCRIBE component_request` |
| DEFAULT | State defaults, numeric zeros and `inventory.last_updated` timestamp | `DESCRIBE` output / schema DDL |
| CHECK | Dates, nonnegative/positive quantities, approval/receipt ranges, distinct labs, paired receipt fields | Run one expected CHECK failure in `demo/01` |
| AUTO_INCREMENT | Surrogate identifiers for 11 principal relations | Inspect `Extra` column in `DESCRIBE` |
| ENUM/domain | Four roles; account, inventory, request, item, transfer and approval states | Inspect DDL/column definition; explain finite workflow domains |
| Joins | All seven views and queries 7–19 in `07_verification_queries.sql` | Run the complete-concept request → transfer → stock JOIN |
| Outer join | Request-to-transfer demonstration and nullable receiving user in views | Explain why requests without transfers/receiver remain visible |
| Subquery | Scalar KPI subqueries in `repositories/report_repository.py` | Explain independent grains preventing join multiplication |
| Views | Seven named views with explicit row grains | Run low-stock or request-progress view |
| Indexes | Justified operational indexes in `02_indexes.sql` | `SHOW INDEX`; compare with `EXPLAIN` in `demo/03` |
| Aggregate | `SUM`, `COUNT`, `COALESCE`, `ROUND`, `DATEDIFF` in views/KPIs | Demand-by-component query or dashboard totals |
| GROUP BY | Component stock, request progress, demand and lab totals | Verification queries 16 and 18 |
| Transaction | `session_scope()` and stock-changing services; seed transaction | Explain atomic reservation/receipt/disposal |
| Rollback | Context-managed rollback plus `demo/02_transaction_demo.sql` | Show value inside transaction, ROLLBACK, restored value |
| Row locking | `SELECT ... FOR UPDATE` through sorted inventory helper | Point to repository and approval/receipt service |
| Stored function | `fn_inventory_available_value` | `SELECT fn_inventory_available_value(5, 12.50);` |
| Stored procedure | `sp_component_availability` | `CALL sp_component_availability(1, NULL);` |
| Trigger | Two narrow inventory/location same-lab triggers | Inspect trigger; run safe expected cross-lab failure if desired |
| Normalization | LAB_CONTACT, USER_PHONE, REQUEST_ITEM, TRANSFER_ITEM; relation-by-relation proof | Open `NORMALIZATION_PROOF.md` |
| Referential integrity | RESTRICT history/master dependencies; CASCADE owned line/value rows | Explain why a referenced inventory/disposal history cannot be casually removed |
| Concurrency control | Stable lock order, recheck-after-lock, one transaction per workflow | Describe competing approval/disposal scenario |
| RBAC | Role/account/lab checks in services/API and role-filtered Next.js/Streamlit navigation | Attempt Faculty transfer approval at API/service/UI boundary |
| Parameterization | SQLAlchemy expressions and bound parameters; report view name allowlist | Contrast bound values with string-concatenated user SQL |
| CSV/reporting | SQL-view data, stable DataFrame output and formula neutralization | Download CSV and inspect header/filtered rows |
| Relational algebra/set operations | `academic_demo/sql/01_relational_algebra_examples.sql` | Run selection/projection/rename/UNION/INTERSECT/EXCEPT/bounded product |
| Correlated/EXISTS/CTE/window | `academic_demo/sql/04_nested_correlated_queries.sql` | Run own-lab average, never-requested and DENSE_RANK examples |
| Cursor | `academic_demo/sql/07_cursor_demo.sql` | CALL isolated procedure; compare with its set-based GROUP BY |
| Trigger audit concept | `academic_demo/sql/08_trigger_audit_demo.sql` | Show demo schema name and audit rows; confirm production remains 13 relations |
| SAVEPOINT/TCL | `academic_demo/sql/09_transactions_savepoints.sql` | Run savepoint rollback, commit and full rollback |
| Deadlock education | `academic_demo/sql/11_deadlock_demo.sql` | Use only two disposable demo rows in two tabs or explain the cycle |
| DCL | `academic_demo/sql/12_dcl_roles_privileges.sql` | Authorized, sanitized CREATE ROLE/GRANT/REVOKE/SHOW GRANTS demonstration |
| NoSQL/CAP | `academic_demo/nosql/` | Explain optional MongoDB CRUD and why relational MySQL remains canonical |

For the complete Unit I–V and Assignment 1–10 mapping, use `ETCS302_SYLLABUS_TRACEABILITY_MATRIX.md`.

## EXPLAIN vocabulary

- **Full table scan:** the optimizer reads the table because no useful/selective index is chosen; acceptable for tiny seed tables but not automatically ideal at scale.
- **Index lookup/range:** the plan uses a key to locate a subset of rows or date/status range.
- **Join key:** PK/FK columns connect rows; `ref`/`eq_ref` access commonly indicates indexed equality joins.
- **Selectivity:** the fraction of rows filtered by a value. A status with few distinct values may be weak alone but useful with lab/date columns.

Do not present invented timing or speedup percentages. `EXPLAIN` shows a plan estimate; it does not prove benchmark performance.
