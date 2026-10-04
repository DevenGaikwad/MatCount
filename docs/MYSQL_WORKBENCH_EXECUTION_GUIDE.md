# MySQL Workbench Execution Guide

**Project:** Smart Electronics Management System (SEMS)  
**Server:** MySQL Community Server 8.4.11 LTS  
**Full-project database:** `sems_db`

MySQL Workbench is the graphical SQL client used to create, inspect and demonstrate the database. It is not the database server, and neither the FastAPI/Next.js application nor the preserved Streamlit fallback requires Workbench to remain open.

## Before execution

1. Start the Windows **MySQL84** service from Services, or confirm that MySQL Server is already running.
2. Open MySQL Workbench and open the local MySQL 8.4 connection.
3. Open a new SQL tab and execute:

   ```sql
   SELECT VERSION();
   ```

4. Confirm that the result reports MySQL 8.4.11. If another version appears, record the actual version rather than editing screenshots or documentation.

## First database build

Use **File → Open SQL Script**, then execute each complete file in this order:

1. `sql/00_database_setup.sql`
2. `sql/01_schema.sql`
3. `sql/02_indexes.sql`
4. `sql/03_views.sql`
5. `sql/04_routines.sql`
6. `sql/05_triggers.sql`
7. `sql/06_seed_data.sql`
8. `sql/07_verification_queries.sql`

Use the lightning-bolt **Execute** control for the complete script. No table-definition editing should be necessary. If a script reports an error, stop at that file, preserve the exact error text, and do not continue as if it succeeded.

## Schema inspection checklist

1. In the **SCHEMAS** panel, select **Refresh All**.
2. Expand `sems_db`.
3. Expand **Tables** and confirm exactly these 13 relations:

   `lab`, `lab_contact`, `user`, `user_phone`, `component_category`, `component`, `storage_location`, `inventory`, `component_request`, `request_item`, `transfer`, `transfer_item`, `disposal_record`.

4. Expand representative tables and inspect **Columns**, **Indexes**, **Foreign Keys**, and **Triggers** where relevant.
5. Expand **Views** and confirm the seven `v_...` reporting views.
6. Expand **Stored Procedures** and **Functions** to inspect the limited academic routines.
7. Do not use Reverse Engineer to redesign the schema. If used, it is visual confirmation only; the frozen ER/EER remains authoritative.

## Verification and faculty demonstration

Run `sql/07_verification_queries.sql`. It demonstrates:

- server and database identity;
- all 13 tables;
- representative structures, PKs, FKs, UNIQUE and CHECK constraints;
- seeded record counts;
- inventory/component/laboratory/location joins;
- request, transfer, allocation and disposal records;
- low-stock, request-progress, transfer-detail and overdue-return views;
- inventory valuation, role data and aggregate demand;
- a complete request-to-transfer multi-table join;
- available views, routines and triggers.

Recommended classroom order:

1. Show `SELECT VERSION()` and `SELECT DATABASE()`.
2. Expand all 13 tables under `sems_db`.
3. Explain PK/FK structure in `inventory`, `component_request` and `transfer`.
4. Run one meaningful JOIN and one view query.
5. Show representative seeded records.
6. Start FastAPI and Next.js separately using `docs/setup_guide.md` (or start the Streamlit fallback only for parity verification).
7. Perform one safe application action.
8. Return to Workbench and execute the corresponding `SELECT` query to prove that both clients use the same MySQL database.

### Optional DBMS demonstrations

After scripts `00`–`06` have succeeded:

1. Open `sql/demo/01_constraint_demo.sql`. Select and execute **one** statement marked `EXPECTED FAILURE`, then run only its following `SELECT`. The error is the expected evidence that a UNIQUE, FK or CHECK rule rejected invalid data. Do not execute the whole file with an “ignore errors” setting.
2. Run all of `sql/demo/02_transaction_demo.sql`. The last column, `rollback_restored_original`, must be `1`; the seeded value is restored.
3. Run `sql/demo/03_index_and_explain_demo.sql`. Expand each result and discuss access type, candidate/selected key, examined rows and join key. Do not claim performance timings from `EXPLAIN`.
4. Under **Tables → representative table → Indexes**, compare the selected key with `sql/02_indexes.sql`.

### ETCS302 advanced academic demonstration pack

The production build remains scripts `00`–`07` above. The separate `academic_demo/sql/` directory adds syllabus evidence without changing the 13-relation boundary. Read `academic_demo/README.md` before execution.

Recommended order after `sems_db` is verified:

1. `01_relational_algebra_examples.sql` — read-only selection/projection/set/join examples on `sems_db`.
2. `02_dml_and_advanced_selects.sql` — mutations affect only a session-local TEMPORARY table.
3. `03_joins_aggregates.sql` and `04_nested_correlated_queries.sql` — read-only advanced SQL.
4. `05_views_indexes_explain.sql` — read-only plans; its bounded `EXPLAIN ANALYZE` executes a SELECT but performs no mutation.
5. `00_ddl_vendor_equivalents.sql` — disposable DDL in `sems_academic_demo` only.
6. `06_stored_routines.sql` — creates only demo routines; reads production views/routines.
7. `07_cursor_demo.sql` — creates a demo procedure/temporary output and contrasts it with set SQL.
8. `08_trigger_audit_demo.sql` — creates validation/synchronization/audit teaching tables/triggers only in `sems_academic_demo`.
9. `09_transactions_savepoints.sql` — isolated COMMIT/ROLLBACK/SAVEPOINT evidence.
10. `10_concurrency_demo.sql` — run setup once, then execute commented Session A/B blocks manually in two tabs. Do not execute it as one sequential proof.
11. `11_deadlock_demo.sql` — optional two-tab teaching exercise against its two demo rows only; issue `ROLLBACK` after any victim/error.
12. `12_dcl_roles_privileges.sql` — administrator-only. Review and replace placeholder account names locally; never place a password in screenshots/source.

After creating the academic schema, Workbench may show extra **teaching** objects under `sems_academic_demo`. These do not belong to `sems_db` and must never be counted as production SEMS relations. To re-establish the boundary at any time:

```sql
SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'sems_db' AND TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;
```

The result must contain exactly 13 names. The literal demo audit table is deliberately isolated and must not be copied into `sems_db`.

## Workbench and application consistency

Set these application values in `.env` or `.streamlit/secrets.toml`:

- `DB_HOST`
- `DB_PORT`
- `DB_NAME=sems_db`
- `DB_USER`
- `DB_PASSWORD`

Use a dedicated `sems_app` account for normal application operation. Do not hard-code the root password or run either Python interface permanently as MySQL root. Next.js receives only the API URL and no database value.

### Exact browser → FastAPI → MySQL proof

Use a deliberate demo record or quantity, record the “before” value, perform one application action, and run the matching read-only query. For example, before and after a one-unit restock of inventory `1`:

```sql
SELECT inventory_id, quantity_available, quantity_reserved, last_updated
FROM inventory
WHERE inventory_id = 1;
```

For a request created through the professional frontend:

```sql
SELECT cr.request_id, cr.request_status, cr.reason,
       ri.component_id, ri.quantity_requested, ri.quantity_approved
FROM component_request AS cr
JOIN request_item AS ri ON ri.request_id = cr.request_id
WHERE cr.created_by = 4
ORDER BY cr.request_id DESC, ri.request_item_id
LIMIT 10;
```

For a transfer status changed through the professional frontend:

```sql
SELECT t.transfer_id, t.approval_status, t.transfer_status,
       ti.inventory_id, ti.quantity_sent, ti.quantity_received
FROM transfer AS t
JOIN transfer_item AS ti ON ti.transfer_id = t.transfer_id
WHERE t.transfer_id = YOUR_DEMO_TRANSFER_ID;
```

Replace only `YOUR_DEMO_TRANSFER_ID`; do not edit a table definition. Capture the Workbench result only after the actual browser action succeeds.

## Safe rerun or reset

The numbered build scripts are intended for a clean `sems_db`. To rebuild during development:

1. Back up any data that must be retained.
2. Open one Workbench connection and execute:

   ```sql
   SET @sems_reset_confirmation = 'RESET_SEMS_DB';
   ```

3. In the same connection, run the complete `sql/99_reset_database.sql` file.
4. Re-run scripts `00` through `06` in order.
5. Run `07_verification_queries.sql` again.

The reset script refuses to drop the database unless the exact session confirmation is present. It targets only `sems_db`; never substitute a broader or unrelated database name.

## Optional backup and restore

Before a reset, Workbench users may choose **Server → Data Export**, select only `sems_db`, include routines/triggers, and export a self-contained SQL file. Confirm that the export file exists before resetting.

Alternatively, from **Command Prompt** (adjust the installation path if required):

```cmd
"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysqldump.exe" -u root -p --single-transaction --routines --triggers sems_db > sems_db_backup.sql
"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe" -u root -p sems_db < sems_db_backup.sql
```

The second command restores and therefore changes data; use it only for the intended `sems_db` after checking the file and target. Never place a password directly in the command.

## Expected object summary

| Object | Expected after build |
|---|---:|
| Base relations | 13 |
| Reporting views | 7 |
| Stored procedure | 1 |
| Stored function | 1 |
| Triggers | 2 |
| Optional demo scripts | 3 |
| ETCS302 advanced SQL demos | 13 isolated/safety-labelled files |
| Optional NoSQL runtime dependency | 0 |

These are implementation expectations, not claims of execution in this build environment.

## Practical evidence to capture locally

Capture genuine screenshots only after actual execution:

1. MySQL 8.4.11 result from `SELECT VERSION()`.
2. `sems_db` in the SCHEMAS panel.
3. All 13 tables.
4. One table structure showing PK/FK details.
5. Seed-data output.
6. A meaningful JOIN result.
7. A reporting-view result.
8. Next.js dashboard.
9. One working CRUD or workflow page.
10. A Workbench query confirming a change made through Next.js/FastAPI.

Until local execution occurs, these remain evidence instructions—not claimed screenshots or test results.
