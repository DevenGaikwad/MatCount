# SEMS Faculty Demonstration Guide

## Before class

- Complete every item in `LOCAL_ACCEPTANCE_CHECKLIST.md` that is feasible.
- Keep MySQL Server running; open Workbench on `sems_db`; activate `.venv` in VS Code; start FastAPI and Next.js in separate terminals.
- Run `.\scripts\final_acceptance.ps1` beforehand and keep the sanitized PASS summary available.
- Use seeded/demo-only data and locally configured credentials. Never show `.env` or secrets.
- Open `07_verification_queries.sql` and the three `sql/demo` scripts in separate Workbench tabs.
- For an extended ETCS302 viva, pre-open only the required safety-labelled files from `academic_demo/sql/`; do not improvise destructive production SQL.
- Do not claim a screenshot/test result that was not produced locally.

## Recommended 12-minute sequence

| Time | Action | What to say |
|---:|---|---|
| 0:00–0:45 | State problem and objective | “Separate lab registers make quantity, location and movement unreliable. SEMS centralizes discovery and controls the request → approval → transfer → receipt/return → disposal lifecycle; it is more than stock CRUD.” |
| 0:45–1:30 | Show frozen ER/EER | “There are 11 main entities plus LAB_CONTACT and USER_PHONE from multivalued attributes, for exactly 13 relations. REQUEST_ITEM and TRANSFER_ITEM are associative entities.” |
| 1:30–2:15 | Workbench: `SELECT VERSION(); SELECT DATABASE();` and SCHEMAS | “Workbench is an independent SQL client. The Python backend and Workbench use the same MySQL 8.4.11 `sems_db`; Next.js never connects to MySQL directly.” |
| 2:15–3:00 | Expand all 13 tables and seven views | “The five-table Assignment 2/3 subset is not this full schema. The full project preserves 13 relations.” |
| 3:00–3:45 | Inspect INVENTORY/COMPONENT_REQUEST/TRANSFER | “Primary keys identify rows; FKs preserve ownership and lifecycle links. `user` is quoted because it is a MySQL reserved word.” |
| 3:45–4:20 | Run one selected EXPECTED FAILURE in `demo/01` | “This error is the expected result: invalid data was rejected by the database. I execute one failure at a time so the demo remains clear.” |
| 4:20–4:50 | Run one JOIN and one view from `07` | “The JOIN traces request, transfer and source inventory. The view has a documented grain, preventing double-counted totals.” |
| 4:50–5:20 | Optional `demo/02` or `demo/03` | “ROLLBACK restores the value, illustrating atomicity. EXPLAIN shows the optimizer’s selected access path; I do not invent timing gains.” |
| 5:20–5:45 | Show the running architecture | “The browser uses Next.js, then a thin FastAPI transport, existing services, repositories, SQLAlchemy/PyMySQL and MySQL. Workbench need not stay open. Streamlit remains a fallback.” |
| 5:45–6:30 | Login and dashboard | “Passwords are external bcrypt hashes mapped to USER.email. The session is revalidated against role, lab and ACTIVE status.” |
| 6:30–7:10 | Inventory availability | “Availability is cross-lab discovery. Available means free stock; reserved means approved stock awaiting dispatch. On-hand valuation includes both.” |
| 7:10–8:10 | Request workflow | Create/inspect a multi-line request and partial review. “Approved quantity cannot exceed requested; line states derive the header atomically.” |
| 8:10–9:35 | Transfer workflow | Inspect/perform a safe stage. “Administrator approval moves Q from available to reserved. Dispatch reduces reserved only—never available twice. Receipt requires explicit destination selection.” |
| 9:35–10:15 | Return/disposal/report | “Temporary return moves a whole received line back because no returned-quantity field exists. Disposal is Administrator-only and atomic. Reports download safe CSV.” |
| 10:15–11:10 | Return to Workbench | Run the exact SELECT for the browser action. “This changed row is direct integration evidence: Next.js → FastAPI → service → repository → SQLAlchemy → MySQL.” |
| 11:10–11:40 | Show final-acceptance output | “One non-destructive command runs Python/API tests, `_test` safety, live DB identity, frontend type/lint/test/build and secret hygiene. Integration fixtures refuse `sems_db`.” |
| 11:40–12:00 | Limitations/future scope | “I disclose destination-lineage and external-auth limitations. Procurement, QR, AI, IoT and maintenance remain future scope, not hidden MVP modules.” |

## Safe proof queries

Use the exact examples under the persistence-proof section in `MYSQL_WORKBENCH_EXECUTION_GUIDE.md`. Record the before value, make one deliberate Next.js action, then rerun the same SELECT. Do not mutate data solely to manufacture screenshots.

## Extended ETCS302 sequence (additional 8–12 minutes)

| Topic | Safe evidence | Explanation cue |
|---|---|---|
| Relational algebra | selections, projection, INTERSECT/EXCEPT and bounded CROSS JOIN in `01_relational_algebra_examples.sql` | translate algebraic operators to declarative SQL |
| Advanced SQL | aggregate/outer joins, correlated NOT EXISTS, derived table, CTE and DENSE_RANK | justify each query by a real SEMS reporting question |
| Optimization | plan comparisons in `05_views_indexes_explain.sql` | an index is justified by access pattern/selectivity; small tables may rationally scan |
| Routine/function | CALL demo procedure with IN/OUT, then SELECT deterministic function | do not duplicate stock transaction logic in stored code |
| Trigger | inspect two production validation triggers; run isolated audit/sync demo only if time permits | audit teaching table is not relation 14 |
| Cursor | CALL cursor stock summary, then run set-based equivalent | cursor meets Assignment 9; set SQL is preferred in production |
| TCL/concurrency | savepoint rollback, then two-tab `FOR UPDATE` allocation | Session B waits/rechecks, preventing over-allocation |
| Deadlock/recovery | explain or use two disposable rows; show full rollback | InnoDB detects a cycle and chooses a victim; undo/redo/checkpoint theory is documented |
| DCL/RBAC | SHOW GRANTS for locally prepared demo roles, then show Student API denial | DB-user privileges and application roles are different layers |
| NoSQL/CAP | show optional sanitized Mongo script/JSON without changing runtime | flexible document metadata may fit MongoDB, but MySQL remains transactional source of truth |

If class time is short, demonstrate cursor + transaction/locking + RBAC and refer faculty to `ETCS302_SYLLABUS_TRACEABILITY_MATRIX.md` for the full map.

## Constraint explanation script

For duplicate category:

1. Say: “The category name is a candidate key enforced by UNIQUE.”
2. Execute only EXPECTED FAILURE 1.
3. Read the error briefly.
4. Run its count SELECT and say: “The count remains one; invalid DML did not damage data.”

## If something fails during class

- Do not edit DDL live without diagnosis.
- Read the safe error and show the relevant check in `preflight_check.py`.
- If MySQL is unavailable, show source/static evidence but state that live proof is incomplete.
- Never switch to SQLite/mock data and present it as MySQL proof.

## Closing sentence

“SEMS demonstrates normalized relational design, constraints, views, indexes, routines, triggers, transaction isolation/rollback, row locking, RBAC and a professional browser-to-MySQL application while keeping the scope implementable and viva-explainable.”
