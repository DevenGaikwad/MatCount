# SEMS Artifact Manifest

**Manifest date:** 2026-08-24  
**Baseline:** v1.0 — unchanged  
**State:** v2 academic/premium source complete; fresh local MySQL, package and human visual/role acceptance pending

## Authoritative governance

| Path | Purpose | State |
|---|---|---|
| `docs/SEMS_BASELINE_FREEZE_REGISTER_v1.0.md` | Frozen 13-relation baseline | Authoritative; unchanged |
| `docs/PROJECT_STATE.md` | Current resumable checkpoint | Current |
| `docs/DECISION_LOG.md` | Decisions through SEMS-DEC-038 | Current |
| `docs/CHANGELOG.md` | Controlled implementation history | Current |
| `docs/FRONTEND_MODERNIZATION_AUDIT.md` | Required A–S decision audit | Complete |
| `docs/PROFESSIONALIZATION_REPORT.md` | Final 39-item modernization report | Current handoff report |
| `docs/PREMIUM_UI_ETCS302_GAP_AUDIT.md` | Required A–AF v2 starting audit | Complete |
| `docs/ULTIMATE_ACADEMIC_PROFESSIONALIZATION_REPORT.md` | Required 47-item v2 handoff | Generated with pending local gates disclosed |

## Database and Workbench

| Path/group | Purpose | State |
|---|---|---|
| `sql/00_database_setup.sql`–`sql/07_verification_queries.sql` | Ordered Workbench setup, 13-relation schema, indexes, views, routines, triggers, seed and read-only proof | Static PASS; historically user-executed; fresh proof pending |
| `sql/99_reset_database.sql` | Explicitly guarded development reset | Excluded from automatic acceptance |
| `sql/demo/` | Constraint, rollback and EXPLAIN demonstrations | Static PASS |
| `scripts/validate_sql_contract.py` | Exact frozen SQL-object contract | Executed PASS |
| `scripts/check_live_database.py` | Read-only MySQL 8.4/`sems_db`/object identity gate | Source complete; local run pending |
| `docs/MYSQL_WORKBENCH_EXECUTION_GUIDE.md` | Windows execution and faculty proof | Complete |

## ETCS302 advanced academic evidence

| Path/group | Purpose | State |
|---|---|---|
| `academic_demo/sql/00`–`12` | DDL/vendor equivalents, algebra, DML, joins, nested queries, optimization, routines, cursor, triggers, TCL, concurrency, deadlock and DCL | Source/static PASS; safety-labelled |
| `academic_demo/nosql/` | Optional sanitized MongoDB CRUD/projection and CAP/model comparison | Present; no runtime dependency |
| `docs/ETCS302_SYLLABUS_TRACEABILITY_MATRIX.md` | Unit/Assignment implementation-to-evidence map | Complete |
| `docs/DBMS_ACADEMIC_COVERAGE_REPORT.md` | Unit I–V and Assignment 1–10 demonstration/viva report | Complete |
| `docs/NORMALIZATION_PROOF.md` | 13-relation keys, FDs, MVDs and normalization proof | Expanded; controlled exceptions disclosed |
| `docs/QUERY_OPTIMIZATION_REPORT.md` | Index/selectivity/EXPLAIN protocol | Complete; local plans pending |
| `docs/TRANSACTION_CONCURRENCY_RECOVERY_REPORT.md` | ACID, locking, schedules, deadlock and recovery | Complete |
| `docs/RBAC_PERMISSION_MATRIX.md` | Page/API/service/action/field/export policy | Complete |

## Python backend and API

| Path/group | Responsibility | State |
|---|---|---|
| `config/`, `db/`, `repositories/`, `services/` | Existing settings, mappings, persistence and business/transaction authority | Preserved; regression PASS where server-independent |
| `api/main.py`, `api/routes/` | Thin FastAPI application and typed module adapters | Added; import/API tests PASS |
| `api/session_store.py`, `api/dependencies.py` | Opaque bounded sessions and actor revalidation | Added; tests PASS |
| `api/errors.py`, `api/serialization.py`, `api/schemas.py` | Safe errors, JSON conversion and typed inputs | Added; tests PASS |
| `requirements.txt` | Python/Streamlit/FastAPI locked ranges | Updated |

## Canonical frontend and fallback

| Path/group | Responsibility | State |
|---|---|---|
| `frontend/app/` | Login, shell and 10 authenticated module routes | Added; build PASS |
| `frontend/features/` | Dashboard, masters, inventory, requests, transfers, disposal and reports | Added; type/lint/build PASS |
| `frontend/components/`, `frontend/lib/`, `frontend/types/` | Design system, auth/API/data utilities and contracts | Added; tests/static scan PASS |
| `frontend/package.json`, `frontend/package-lock.json` | Reproducible Node dependency/scripts | Added |
| `frontend/.env.local.example` | Browser-visible non-sensitive API address only | Added; scan PASS |
| `app.py`, `pages/`, `ui/`, `.streamlit/` | Known-good Streamlit fallback | Preserved |

## Validation and automation

| Path | Purpose | Current evidence |
|---|---|---|
| `tests/` | Unit, contract, architecture, API, RBAC and MySQL integration coverage | 131 server-independent PASS; 20 MySQL-only pending |
| `frontend/lib/*.test.ts` | Frontend role/navigation/capability and display-format contracts | 10 PASS |
| `scripts/preflight_check.py` | Local configuration/import readiness | Extended for modern artifacts |
| `scripts/test_database_safety.py` | Safe `_test` target guard | Missing target correctly fails here |
| `scripts/scan_secrets.py` | Secret/client-DB/package scan | PASS |
| `scripts/validate_project.py` | Server-independent Python/SQL/secret validation | PASS |
| `scripts/final_acceptance.ps1` | Canonical Windows complete acceptance | Created; PowerShell/local DB run pending |
| `.github/workflows/ci.yml` | Future Python and frontend CI | Prepared; not published/run remotely |

## Documentation

README, architecture, setup, user manual, workflow, schema/cardinality/normalization, traceability, test/validation, Workbench, faculty demo, viva, screenshot, known-issues, final-audit and local-acceptance documents are present. Modernization is consistently classified as a **presentation/API architecture change**, not a database revision.

## Release artifact policy

The v2 handoff archive is `SEMS_Final_Academic_Professional_Release_v2.zip`. It contains source, SQL, academic demos, tests, scripts, examples and documentation. It excludes `.venv`, `node_modules`, `.next`, `.env`, private Streamlit secrets, caches, logs, exports and other generated/private files. Its filename identifies the enhanced package; it does not assert final academic acceptance.

The earlier `SEMS_Final_Professional_Release.zip` remains an unaccepted intermediate archive. Keep/archive it until v2 checksum, extraction and complete local acceptance succeed; only then is it safe to delete if the user chooses.

The historical `SEMS_Release_Candidate.zip` remains the protected rollback archive and is not overwritten.

## Evidence rule

Static validation is not live MySQL execution. A skipped integration case is not a pass. A successful production build is not human visual acceptance. No screenshot, public URL, repository publication or final-release claim is fabricated.

## Publication and offline RC2 addendum — 2026-10-04

The preceding August checkpoint is historical. The live repository has successful remote CI; the current source freeze and actual release evidence are separate records.

| Path/group | Purpose | Evidence boundary |
|---|---|---|
| `docs/OFFLINE_FACULTY_DEMONSTRATION_BASELINE.md` | Original v2/RC1 hashes, exact 33-path parity and commit mapping | Independently verified provenance |
| `docs/RC2_FREEZE_REVIEW.md` | Reviewed dependency/security/tooling decisions | Native legacy-plugin peer warnings disclosed |
| `FACULTY_DEMO_START_HERE.md`, `OFFLINE_SETUP_WINDOWS.md` | Frozen local Windows faculty instructions | Intended-host execution pending |
| `DEPENDENCY_VERSIONS.md`, `requirements-*.lock.txt` | Exact runtime/dependency record and hashed Python wheels | Platform-specific installation checked by CI |
| `VALIDATION_SUMMARY.md` | Scope and pending acceptance | Not a final academic acceptance report |
| `scripts/package_offline_demo.py`, `scripts/validate_offline_candidate.py` | Exact Git-source packaging and clean extracted-source gates | Reports generated externally from actual results |
| `.github/workflows/offline-prerelease.yml` | Windows checks, restricted prerelease publication and fresh asset-download verification | No repository-admin or public-visibility authority |

RC2 includes all source, SQL, academic material, tests, examples and runbooks. Its external ZIP checksum, complete per-file manifest and observed validation report avoid self-hashing. Preserve the unchanged original v2 and RC1 bytes privately; demonstrate an immutable reviewed candidate rather than the moving `main` branch.
