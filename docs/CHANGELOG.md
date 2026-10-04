# SEMS Changelog

All notable controlled changes are recorded here. This is a project-state log, not evidence of database execution.

## 2026-08-21 — Baseline v1.0 freeze recovery

### Added

- Project Workspace Recovery Audit.
- SEMS Baseline Freeze Register v1.0 in Markdown and DOCX.
- PROJECT_STATE checkpoint.
- DECISION_LOG.
- CHANGELOG.
- ARTIFACT_MANIFEST.

### Corrected

- Transfer approval now atomically moves approved quantity from `quantity_available` to `quantity_reserved`.
- Dispatch now reduces reserved quantity only and does not subtract available quantity again.
- Pre-dispatch cancellation/rejection releases reservation back to available.
- Receipt and temporary return require explicit destination inventory/location selection and validation without adding a destination FK.
- `condition_on_return` is reserved for actual return, not receipt.

### Confirmed

- Phase 0 complete.
- Phase 1 now complete.
- Exactly 13 MVP relations.
- MySQL Community Server 8.4.11 LTS target.
- No SQL, Python, tests, Git repository or deployment existed or was assumed.

### Excluded

- Unrelated `quality_dashboard_db` SQL artifact.
- Duplicate-format files as independent authorities.
- Assignment 2/3 five-table subset as the full architecture.
- All frozen future-scope modules.

### Stopped

- Phase 2 was not started. Explicit approval is required.

## 2026-08-21 — Integrated implementation authorization and Phase 2

### Authorized

- Baseline v1.0 approved.
- Phases 2–12 authorized as one controlled implementation cycle.
- MySQL Workbench approved for backend execution, inspection and faculty demonstration.
- Central DESPU-inspired orange-and-white Streamlit theme approved without protected branding assets.

### Added

- `sql/00_database_setup.sql` through `sql/07_verification_queries.sql`.
- Guarded `sql/99_reset_database.sql` development reset.
- Exactly 13 frozen table definitions, justified indexes, seven reporting views, two limited routines and two narrow inventory-location triggers.
- Coherent seed data covering all four roles and representative request/transfer/return/disposal scenarios.
- Static SQL contract validator.
- MySQL Workbench execution and demonstration guide.

### Validated

- Static SQL contract passed for all nine scripts, 13 relations and seven views.
- No forbidden `password_hash`, `destination_inventory_id`, `lab_status` or future-scope relation was added.

### Not yet validated

- Scripts have not been executed against MySQL because no MySQL client/server exists in the current execution environment.

## 2026-08-21 — Phases 3–10 application implementation checkpoint

### Phase 3 — Connectivity and repositories

- Added environment/Streamlit-secret settings, constants and safe rotating logging.
- Added pooled SQLAlchemy engine/session/healthcheck and exactly 13 ORM mappings.
- Added persistence-only laboratory, user, component, inventory, request, transfer, disposal and reporting repositories.
- Verified MySQL ORM compilation quotes the frozen `user` relation.

### Phase 4 — Authentication and RBAC

- Added external bcrypt demonstration authentication mapped by USER.email.
- Added active-account, role, single-lab and transfer-side scope enforcement.
- Added role-filtered Streamlit navigation while retaining service-level authorization.

### Phase 5 — Master data

- Added laboratory, user, component/category and storage-location pages and services.
- Added null-normalized storage-coordinate checks and omitted LAB activation.

### Phase 6 — Inventory

- Added cross-lab availability, scoped registration, restocking, physical move/cost update and operational status control.
- Preserved free/reserved meanings and same-lab storage validation.

### Phase 7 — Requests

- Added multi-line DRAFT creation, submission, complete line review, partial/full approval and derived header status.

### Phase 8 — Transfers

- Added approved-request allocation, reservation, rejection/cancellation, reserved-only dispatch, explicit destination receipt and line-complete temporary returns.
- Used transaction boundaries, stable inventory lock ordering and no destination-inventory attribute.

### Phase 9 — Disposal

- Added Administrator-only, row-locked disposal event and free-stock decrement.

### Phase 10 — Dashboard and reports

- Added role-scoped KPIs, seven SQL-view reports, focused Plotly charts and CSV downloads.
- Added centralized orange/white academic styling without university logos or copied assets.

### Validation checkpoint

- Python compile/import checks passed.
- Streamlit login-shell AppTest passed with no exception.
- Pytest checkpoint: 60 passed; 14 MySQL-only tests skipped for absent test URL.

## 2026-08-21 — Phase 11/12 validation and documentation checkpoint

### Added

- Completed server-independent unit, contract, architecture, transaction-design and database-builder test coverage.
- Expanded MySQL integration coverage for schema, seed, views, constraints and same-lab trigger behavior.
- Added implementation-aligned architecture, schema dictionary, cardinality, workflow, Windows setup and user documentation.
- Added test plan, known-issues register and honest validation report.

### Validated

- Static SQL contract: PASS for nine scripts, exactly 13 frozen relations and seven views.
- Python compile/import and dependency compatibility: PASS.
- Pytest: 61 passed, 14 MySQL-only tests skipped, 0 failed.
- Direct console-script test execution and complete numbered-script splitting were regression-checked after the final packaging fixes.
- Streamlit login-shell AppTest: PASS with zero exceptions.
- Streamlit process startup health check: PASS with HTTP 200 `ok`.

### Pending local evidence

- No MySQL 8.4.11 server/client was available, so DDL/DML execution and 14 integration tests are not claimed as passed.
- Workbench screenshots and backend-confirmation evidence remain genuine local user actions.
- Resume checkpoint: Phase 11 local MySQL integration verification.

### Corrected during final packaging

- Added the repository root to pytest configuration so both `pytest` and `python -m pytest` resolve project packages consistently.
- Updated the SQL build splitter to ignore standalone/trailing comments while continuing to reject genuinely incomplete statements.
- Clarified that ALLOCATED is a REQUEST_ITEM state, not a COMPONENT_REQUEST header state.
- Hardened empty-master UI states and limited Lab Assistant inventory action selectors to their own laboratory.
- Created a clean Phase 2–12 handoff archive without virtual environments, caches, secrets or runtime logs.

## 2026-08-22 — MAX-QUALITY HARDENING PASS

### Corrected

- Aligned transfer RBAC with the latest frozen decision: Administrator approval/rejection; Faculty monitoring; Lab Assistant/Administrator operational execution/cancellation.
- Removed Student access to transfer detail and restricted Student request-progress reporting/dashboard data to the creator.
- Corrected total on-hand valuation to include available plus reserved stock.
- Added stale/tampered session database revalidation.
- Added DRAFT/SUBMITTED request cancellation and froze request review after allocation begins.
- Reused same destination positions during multi-line receipt and rejected no-new-quantity receipt confirmations.
- Prevented blocking/deactivating inventory with outstanding reservations.
- Hardened validation for IDs, quantities, money, dates, email/phone, text length and nullable storage coordinates.
- Added CSV spreadsheet-formula neutralization and safe configuration placeholder/timeout checks.

### Added

- Three optional faculty SQL demonstrations for constraints, rollback and EXPLAIN.
- `preflight_check.py` and `validate_project.py` with a strict `_test` database guard for local acceptance.
- Expanded unit/contract/integration source tests, including role bypass, stale sessions, cancellation, NULL storage, valuation, routines, indexes and trigger update behavior.
- Optional future GitHub Actions workflow using server-independent validation only; nothing was published.
- Implementation consistency, normalization, ER mapping, DBMS feature, traceability, failure-recovery, faculty demo, viva, local acceptance, screenshot and final-audit documents.
- Workbench proof queries, backup/restore guidance and exact evidence plan.

### UI/analytics

- Added named Administrator source-lab and receipt/return destination selectors where role scope permits.
- Added responsive spacing and visible focus state while preserving the orange/white Streamlit design.
- Added available-only and on-hand valuation columns with explicit grains; corrected empty-request aggregate counts and overdue partial-receipt visibility.

### Validation actually performed

- Python compile and AST parse: PASS.
- SQL static contract: PASS for 13 tables, seven views, nine support scripts and three demos.
- Architecture/static boundary and secret-template scans: PASS.
- Pure business-rule/validation sanity: PASS.
- Post-hardening pytest/Streamlit: NOT RUN because required packages are unavailable in the rebuilt disposable sandbox.
- MySQL 8.4.11/Workbench: NOT RUN; no client/server exists here.

### Governance

- Baseline remains v1.0; no relation, attribute, PK/FK or state domain was added.
- Phase 13 local preparation is complete; Phase 14 source/static audit is provisional.
- Prepared a clean provisional source handoff named `SEMS_Release_Candidate.zip`; the archive name is not a release-acceptance claim.
- No GitHub remote, deployment, license, public URL or screenshot was created/fabricated.

## 2026-08-23 — PROFESSIONAL FRONTEND MODERNIZATION

### Architecture

- Selected Next.js + React + TypeScript + Tailwind as the canonical presentation source after completing `FRONTEND_MODERNIZATION_AUDIT.md`.
- Added a thin FastAPI boundary over the existing services. API routes contain no repository, SQLAlchemy, PyMySQL or raw-SQL access.
- Added bounded opaque bearer sessions with current database-actor revalidation, explicit local CORS/trusted-host configuration and sanitized errors.
- Preserved the complete Streamlit implementation as a fallback; no frozen database table, column, key, relationship, state or transaction rule changed.

### Professional interface

- Added an institutional split login, responsive authenticated shell, role-aware grouped navigation, user/lab context and reusable icon/design-system components.
- Added professional dashboard metrics/charts and complete pages for laboratories, users, catalogue, storage, inventory, requests, transfers, disposal and reports.
- Implemented searchable/sortable/paginated tables, validated forms, dialogs, loading/error/empty states, status/role badges, responsive layouts and keyboard-visible focus.
- Implemented request-line building/review, transfer lifecycle workspaces, typed disposal confirmation and report-grain guidance with formula-safe CSV download.

### Workflow support

- Added an approved-request transfer-plan read method for Lab Assistant/Administrator so cross-lab source allocation can show only approved components without weakening ordinary request-detail scope.
- Added a scoped transfer-detail reporting query so dispatch/receipt/return forms can show component identities without persisting any new destination attribute.

### Validation and handoff

- Added FastAPI contract/session tests and frontend permission tests.
- Added `scripts/check_live_database.py`, `scripts/test_database_safety.py`, `scripts/scan_secrets.py` and mandatory `scripts/final_acceptance.ps1`.
- Added a locked npm dependency graph and expanded future CI to type-check, lint, test and build the frontend.
- Fresh source-environment results: 114 server-independent Python/API cases pass; 10 API-selected cases pass; strict TypeScript, zero-warning ESLint, 8 Vitest checks and optimized Next.js production build pass.
- Fresh MySQL 8.4.11, all integration tests, human visual/role workflows and screenshots remain local acceptance gates and are not fabricated.

## 2026-08-24 — ULTIMATE ACADEMIC + PREMIUM UI v2 ENHANCEMENT

### Security and multi-user authorization

- Added one server-side financial/data-minimization policy used before API serialization and CSV export.
- Student and Faculty responses now omit all cost/valuation fields; Student availability additionally omits storage coordinates and reserved/accounted quantities.
- Restricted raw inventory positions and storage locations to operational roles and restricted user/phone enumeration to Administrator.
- Added direct API-bypass, service-bypass, financial-response and export tests.
- Added a shared frontend capability map for financial, inventory, request, transfer, disposal and global-report presentation decisions.

### ETCS302 academic depth

- Added 13 safety-labelled SQL demonstrations covering vendor-specific DDL, relational algebra/set operations, DML predicates, joins/aggregates, nested/correlated queries, CTE/window functions, EXPLAIN ANALYZE, procedures/functions, cursor, trigger audit concept, savepoints, concurrency, deadlock and DCL.
- Added an optional sanitized MongoDB CRUD/projection extension and CAP/NoSQL comparison with zero production runtime dependency.
- Extended the static SQL contract to verify all teaching files while continuing to require exactly 13 production relations and seven views.
- Added architecture/data-model, FD/normalization, query-optimization, transaction/concurrency/recovery, RBAC, syllabus traceability and Unit/Assignment coverage reports.
- Expanded Workbench, faculty demonstration, viva and genuine screenshot plans for Assignments 1–10.

### Premium frontend

- Refined design tokens, typography, institutional navy/orange login, dark navigation shell, role/lab context, dashboard hero, quick actions, operational pulse, cards and responsive behavior.
- Hardened the modal with unique labels, focus trap/restoration, Escape handling and scroll lock.
- Enhanced shared tables with sticky headers, column visibility, density, accessible sorting/caption, keyboard selection, ranges and paging.
- Added skeleton loading and role-policy notices; removed backend/credential jargon from user-facing service state.
- Evaluated current accessible primitives and retained the existing dependency-light component system; no package was added solely for appearance.

### Validation actually performed

- Static SQL/ETCS302 contract: PASS — 13 production relations, seven views, 13 academic SQL demos and optional NoSQL extension.
- Server-independent Python/API: **131 passed, 20 MySQL integration cases deselected, 0 failed**.
- Broad collection without a test URL: **131 passed, 20 skipped, 0 failed**.
- API-selected: **17 passed, 0 failed**.
- Focused RBAC/data-policy/API suite: **30 passed, 0 failed**.
- Frontend: TypeScript PASS; ESLint PASS with zero warnings; Vitest **10 passed**; optimized production build PASS with 14 routes.
- Secret scan and Python dependency consistency: PASS.
- Fresh npm vulnerability audit: BLOCKED in this sandbox by network policy; retained as mandatory Windows acceptance check.
- Browser-rendered QA: BLOCKED by absence of a browser executable; source/build/accessibility review completed and human visual acceptance remains mandatory.
- Fresh MySQL 8.4.11/Workbench and `sems_test` integration: NOT RUN here and not claimed.
