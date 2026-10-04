# SEMS ETCS302 Academic Demonstrations

This directory contains syllabus evidence that should not inflate or endanger the canonical `sems_db` production schema.

## Safety classes

- **SAFE FOR `sems_db`** — read-only statements or session-local temporary tables only.
- **ACADEMIC DEMO SCHEMA ONLY** — creates or changes objects only in `sems_academic_demo`.
- **MANUAL TWO-SESSION DEMO** — run only the labelled blocks in separate Workbench tabs.
- **ADMINISTRATOR-ONLY DCL DEMO** — creates MySQL roles/users and must be reviewed before execution.

The production boundary remains exactly 13 base relations and seven reporting views. These scripts do not run automatically during application setup or acceptance.

## Recommended faculty sequence

1. `sql/01_relational_algebra_examples.sql`
2. `sql/02_dml_and_advanced_selects.sql`
3. `sql/03_joins_aggregates.sql`
4. `sql/04_nested_correlated_queries.sql`
5. `sql/05_views_indexes_explain.sql`
6. `sql/06_stored_routines.sql`
7. `sql/07_cursor_demo.sql`
8. `sql/08_trigger_audit_demo.sql`
9. `sql/09_transactions_savepoints.sql`
10. `sql/10_concurrency_demo.sql` in two Workbench sessions
11. `sql/11_deadlock_demo.sql` only with disposable demo rows
12. `sql/12_dcl_roles_privileges.sql` only from an authorized administrative connection

`nosql/` is an optional, non-runtime MongoDB comparison. It is not required to run SEMS.

