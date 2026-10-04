# SEMS Test Plan

## Objectives

The suite verifies the frozen 13-relation contract, business rules, authorization, transaction design and reporting calculations. It separates server-independent tests from tests that genuinely require MySQL. A skipped integration test is not reported as a pass.

## Test environments

| Environment | Scope | Data safety |
|---|---|---|
| Available build environment | Unit, contract, architecture, FastAPI, compile/import and modern frontend quality/build checks | No MySQL connection required |
| Local MySQL 8.4.11 LTS | DDL, constraints, FKs, CHECKs, triggers, views, seed and workflow persistence | Dedicated database ending in `_test` only |
| Faculty demonstration | Workbench plus Next.js/FastAPI against `sems_db` | Seed/demo data; perform only deliberate reversible operations |

## Automated coverage map

| Area | Representative assertions | Test location |
|---|---|---|
| Frozen model | Exactly 13 mapped/DDL tables; exact PK/FK/attribute boundaries; no forbidden schema additions | `tests/test_models_contract.py`, `tests/test_sql_contract.py` |
| Architecture | Pages do not issue persistence SQL; service/repository boundaries exist | `tests/test_architecture.py` |
| Authentication/RBAC | bcrypt mapping, active account, role permissions and laboratory scope | `tests/test_auth.py`, `tests/test_rbac.py` |
| Session/security | stale database identity, Student transfer bypass, Faculty transfer-approval bypass and database-unavailable behavior | `tests/test_service_security.py`, `tests/test_healthcheck.py` |
| Financial/data minimization | Student/Faculty financial removal, Student availability allowlist and CSV/dashboard redaction | `tests/test_data_policy.py`, `tests/api/test_api_contract.py` |
| Validation | text, IDs/quantities, decimal, email/phone, date and configuration boundaries | `tests/test_validation.py`, `tests/test_settings.py` |
| Inventory | free/reserved rules, non-negative quantities, low-stock and valuation calculations | `tests/test_rules.py`, `tests/test_analytics.py` |
| Requests | non-empty submission, requested/approved limits, derived partial/full/rejected states | `tests/test_rules.py`, `tests/test_workflow_contract.py` |
| Request cancellation | DRAFT/SUBMITTED cancellation and illegal backward transition | `tests/test_request_service.py` |
| Transfers | reservation, release, dispatch, receipt/return contracts, stable locking and transaction boundaries | `tests/test_rules.py`, `tests/test_workflow_contract.py`, `tests/test_transactions.py` |
| Disposal | role restriction, stock-bound checks and transactional decrement contract | `tests/test_rbac.py`, `tests/test_transactions.py` |
| Database builder | clean script ordering, DELIMITER parsing and `_test` safety guard | `tests/test_database_builder.py` |
| MySQL schema | unique/check/FK constraints, 13 tables, views, trigger invariant and seed data | `tests/integration/` |
| Academic DBMS features | routines, indexes, on-hand valuation, partial seed and update trigger | `tests/integration/test_mysql_academic_features.py` |
| FastAPI boundary | authentication requirement, opaque session, safe errors, route-to-service delegation and response enrichment | `tests/api/` |
| Browser/database separation | no API repository bypass; no Node DB dependency/private config; modern routes plus fallback exist | `tests/test_architecture.py`, `scripts/scan_secrets.py` |
| ETCS302 teaching contract | 13 advanced SQL files, safety labels, cursor/TCL/DCL/NoSQL tokens and unchanged 13/7 production boundary | `scripts/validate_sql_contract.py`, `tests/test_sql_contract.py` |
| Frontend role/navigation | role-specific navigation, financial and workflow capability decisions | `frontend/lib/permissions.test.ts` |
| Frontend compilation/quality | strict TypeScript, zero-warning ESLint and production route build | npm `typecheck`, `lint`, `build` |

## Commands

### Canonical complete Windows acceptance

```powershell
.\scripts\final_acceptance.ps1
```

This is the preferred routine gate. It refuses unsafe integration targets and does not rebuild `sems_db`.

### Server-independent suite

```powershell
pytest -m "not integration"
```

### Prepare a dedicated integration database

```powershell
$env:DB_PASSWORD = "LOCAL_TEST_ADMIN_PASSWORD"
python scripts/build_database.py --database sems_test --user root
$env:SEMS_TEST_DATABASE_URL = "mysql+pymysql://root:URL_ENCODED_PASSWORD@127.0.0.1:3306/sems_test?charset=utf8mb4"
pytest
```

The database builder accepts only `sems_db` or a database name ending in `_test`. The integration fixture independently rejects any other database name.

### Supporting checks

```powershell
python scripts/validate_sql_contract.py
python scripts/preflight_check.py --allow-unconfigured --skip-database
python scripts/validate_project.py
python -m compileall app.py config db repositories services ui pages scripts tests
python -m pip check
npm --prefix frontend run typecheck
npm --prefix frontend run lint
npm --prefix frontend run test
npm --prefix frontend run build
npm --prefix frontend audit --audit-level=critical
```

For modern startup, run Uvicorn and Next.js separately, then confirm the login/health state at `http://127.0.0.1:3000`. Streamlit startup remains a fallback parity check.

## Manual acceptance scenarios

| ID | Scenario | Expected result |
|---|---|---|
| A | Administrator manages master data | Valid records persist; FK/duplicate violations are rejected |
| B | Student searches across labs | Availability visible without granting write access to other labs |
| B2 | Student inspects API/report/export | No unit cost, valuation, storage coordinates or reserved/accounted quantity is returned/exported |
| C–D | Student submits multi-line request; Faculty partially approves | Positive unique lines; line results and PARTIALLY_APPROVED header agree |
| E–F | Lab Assistant allocates; Administrator approves | Only valid source rows; available decreases and reserved increases once |
| G–H | Cancel before dispatch or dispatch approved transfer | Cancellation reverses reservation; dispatch decreases reserved only |
| I | Destination receives | Explicit matching destination selected; received delta increments stock once |
| J–K | Temporary line becomes overdue and is returned | Overdue view includes it; complete-line return restores source/destination totals |
| L | Administrator disposes stock | Disposal row and free-stock decrement commit together |
| M | Unauthorized role attempts write | Service rejects operation and transaction leaves no partial changes |
| N | Dashboard/CSV inspected | Totals match SQL-view grain with no double counting |

## Transaction/rollback checks

- Force a later-line failure during a multi-item approval and confirm every earlier stock change rolls back.
- Attempt receipt into the wrong laboratory/component and confirm no destination increment or header progression.
- Attempt excessive disposal and confirm neither inventory nor history changes.
- Run concurrent allocation checks locally where practical; locked inventory rows must be acquired in ascending ID order.

## Recorded results and rerun rule

Pre-hardening checkpoint on 2026-08-21:

- `61 passed`.
- `14 skipped`, all requiring `SEMS_TEST_DATABASE_URL` and a real MySQL test database.
- No failed tests.
- MySQL 8.4.11 execution remains a local verification step.

Post-v2 current source evidence (2026-08-24):

- 131 server-independent Python/API cases passed; 20 MySQL-only cases deselected.
- A broad run without `SEMS_TEST_DATABASE_URL` produced 131 passed and 20 explicitly skipped.
- 17 API-selected cases and a focused 30-case RBAC/data-policy/API selection passed.
- 10 Vitest cases passed.
- TypeScript, zero-warning ESLint and production Next.js build passed.
- Secret scan and Python `pip check` passed.
- Fresh npm vulnerability audit could not run through the sandbox network boundary and remains a mandatory Windows acceptance item.
- Browser-rendered visual QA is pending because no browser executable exists here; source/accessibility/responsive review is documented separately.

Do not report the 20 MySQL cases as passed. The historical user-verified 118/0 predates modernization. The authoritative fresh full-suite number must come from the configured Windows run of `final_acceptance.ps1` and be copied into `VALIDATION_REPORT.md`.

pytest-cov and Ruff were not added: neither was available in the build environment, and adding optional dependency/lint churn without execution evidence would not improve release confidence. Prepared CI runs the actual server-independent validation after dependency installation.
