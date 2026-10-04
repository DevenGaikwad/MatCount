# MatCount

## Smart Electronics Lab and Component Management System

**SEMS v2 source complete · Final Windows/MySQL acceptance pending**

MatCount is the repository and product-facing name of the Smart Electronics Lab and Component Management System, whose implementation and database artifacts retain the established **SEMS** naming convention. This academic full-stack project manages electronic components, laboratory stock, requests, inter-laboratory transfers and faculty SQL demonstrations.

> **Release-candidate boundary:** Source professionalization and server-independent checks are complete. The frozen production design has **13 relations and seven views**. Fresh Windows, MySQL 8.4.11, MySQL Workbench, four-role workflow and genuine visual acceptance are still required. This repository does **not** claim final academic-release acceptance.

> **Security update (2026-10-04):** The original v2 archive remains unchanged as private provenance. This candidate pins patched Next.js 16.3.6 and resolves sharp 0.35.5. The runtime npm audit reports **zero findings**. One unfixed, development-only `braces` advisory affects five tooling packages; an exact CI gate rejects any new advisory or runtime finding. See the [current security review](docs/SECURITY_REMEDIATION_2026-10-04.md) and [original finding](docs/PUBLICATION_READINESS_2026-10-04.md).

| Team member (ascending PRN) | PRN | Project/repository status |
|---|---:|---|
| Aaryan Sachin Anand | 1022411049 | Academic project team member; GitHub invitation pending exact account verification |
| Deven Sachin Gaikwad | 1022411052 | Academic project team member; repository owner `DevenGaikwad` |

Academic context: DES Pune University, School of Engineering and Technology, Department of Electronics and Communication Engineering; academic year 2026–27; ETCS302 DBMS demonstration. No institutional endorsement is claimed. See [AUTHORS.md](AUTHORS.md), [CONTRIBUTORS.md](CONTRIBUTORS.md) and [CITATION.cff](CITATION.cff).

## Quick navigation

| Purpose | Start here |
|---|---|
| Faculty walkthrough | [Faculty demo guide](docs/FACULTY_DEMO_GUIDE.md), [Workbench execution guide](docs/MYSQL_WORKBENCH_EXECUTION_GUIDE.md) |
| Schema and syllabus | [Schema dictionary](docs/schema_dictionary.md), [ETCS302 matrix](docs/ETCS302_SYLLABUS_TRACEABILITY_MATRIX.md) |
| Security and roles | [RBAC matrix](docs/RBAC_PERMISSION_MATRIX.md), [security policy](SECURITY.md) |
| Validation and screenshots | [Current security review](docs/SECURITY_REMEDIATION_2026-10-04.md), [project state](docs/PROJECT_STATE.md), [acceptance checklist](docs/LOCAL_ACCEPTANCE_CHECKLIST.md), [evidence plan](docs/SCREENSHOT_EVIDENCE_PLAN.md) |
| Collaboration | [Contributing](CONTRIBUTING.md), [publication runbook](docs/GITHUB_PUBLICATION_RUNBOOK.md), [changelog](CHANGELOG.md), [release integrity](release/README.md) |

SEMS is a Third-Year B.Tech DBMS mini-project for centralized visibility and controlled movement of electronic components across engineering laboratories. It combines a normalized 13-relation MySQL schema, a modular Python business layer, a thin FastAPI boundary and a professional Next.js/React interface. The preserved Streamlit implementation remains a fallback during final local acceptance.

**Formal title:** Centralized Electronic Component and Laboratory Asset Management System  
**Database:** MySQL Community Server 8.4.11 LTS  
**Full-project database:** `sems_db`  
**Canonical web interface:** `frontend/` + `api/main.py`  
**Preserved fallback:** `app.py` (Streamlit)

## Problem and academic purpose

Engineering laboratories often keep components in disconnected spreadsheets, notebooks or local registers. This makes quantity/location discovery slow, allows duplicate allocation, and leaves request, dispatch, receipt, return and disposal history difficult to reconcile. SEMS models those facts as related, constrained transactions. Its academic purpose is to demonstrate normalized ER/EER mapping, integrity constraints, views/indexes/routines/triggers, ACID transactions, row locking, RBAC and a real MySQL-backed frontend—not only inventory CRUD.

## Implemented MVP

- Four roles: Student, Faculty, Lab Assistant and Administrator.
- Laboratory, contact, user, phone, category, component and storage masters.
- Free/reserved inventory, valuation and low-stock reporting.
- Multi-line component requests and faculty approval.
- Inter-laboratory planning, reservation, dispatch and receipt.
- Temporary return tracking and overdue-return reporting.
- Administrator-authorized disposal.
- Seven SQL views, limited routines, narrow integrity triggers and CSV exports.
- Isolated ETCS302 demonstrations for advanced SQL, cursor, trigger audit, savepoints, concurrency, deadlock, DCL and optional MongoDB CRUD/CAP study.
- Backend-enforced financial minimization: Student/Faculty receive no cost or valuation fields; Student availability also omits coordinates and reserved/accounted quantities.
- Central DESPU-inspired orange/white academic theme without copied logos/assets.

The project intentionally excludes procurement, maintenance, serialized assets, QR infrastructure, AI, IoT and other frozen future-scope modules.

## Technology stack

| Layer | Technology |
|---|---|
| Database | MySQL Community Server 8.4.11 LTS, InnoDB, utf8mb4 |
| SQL client | MySQL Workbench (build, inspection and faculty demonstration) |
| Language/runtime | Python 3.12+ |
| Canonical frontend | Next.js 16 + React 19 + TypeScript 5.9 + Tailwind CSS 4 |
| HTTP boundary | FastAPI + Uvicorn; opaque process-local bearer sessions |
| Preserved fallback | Streamlit |
| Data access | SQLAlchemy 2.x + PyMySQL |
| Data/visualization | pandas + Plotly |
| Authentication adapter | bcrypt hashes in protected local configuration |
| Testing | pytest + FastAPI TestClient + Vitest + TypeScript + ESLint; isolated MySQL `_test` integration suite |

## Frozen 13-relation schema

`LAB`, `LAB_CONTACT`, `USER`, `USER_PHONE`, `COMPONENT_CATEGORY`, `COMPONENT`, `STORAGE_LOCATION`, `INVENTORY`, `COMPONENT_REQUEST`, `REQUEST_ITEM`, `TRANSFER`, `TRANSFER_ITEM`, `DISPOSAL_RECORD`.

REQUEST_ITEM and TRANSFER_ITEM are associative entities; LAB_CONTACT and USER_PHONE normalize multivalued attributes. No password, destination-inventory or LAB-status attribute is silently added.

## Roles

| Role | Main scope |
|---|---|
| Student | Cross-lab catalogue/availability; own-lab request creation/submission and own progress |
| Faculty | Own-lab request review and relevant transfer/report monitoring; no transfer approval/execution |
| Lab Assistant | Own-lab storage/inventory; transfer planning, dispatch, receipt and whole-line return after approval |
| Administrator | Global masters/users, request override, transfer approval/rejection, disposal and all-lab reporting |

Navigation is filtered for usability; services independently enforce ACTIVE status, role, lab scope and current database identity.

## Architecture

```text
Browser → Next.js / React / TypeScript
        → FastAPI transport adapters
        → Python services (RBAC, workflow, transactions)
        → repositories → SQLAlchemy → PyMySQL → MySQL 8.4.11 / sems_db

Preserved fallback: Streamlit pages → the same services → the same sems_db
Independent SQL client: MySQL Workbench → the same sems_db
```

Node.js never connects to MySQL. API routes call services rather than repositories, and the service layer remains the single authority for validation, RBAC and transaction semantics.

MySQL Workbench is an independent SQL client for executing and demonstrating the same `sems_db`. The application never depends on Workbench being open.

## Prerequisites

- Windows 10/11.
- MySQL Community Server **8.4.11 LTS**.
- MySQL Workbench compatible with the installed server.
- Git for cloning the published repository.
- Python **3.12+**.
- Node.js **20.9+** (Node.js 24 recommended for the locked frontend).
- VS Code and its Python extension (recommended).

## Database build in MySQL Workbench

Open and execute complete scripts in this order:

1. `sql/00_database_setup.sql`
2. `sql/01_schema.sql`
3. `sql/02_indexes.sql`
4. `sql/03_views.sql`
5. `sql/04_routines.sql`
6. `sql/05_triggers.sql`
7. `sql/06_seed_data.sql`
8. `sql/07_verification_queries.sql`

Do not use the Assignment 2/3 database `smart_electronics_lab_ddl` for the full project. Follow [docs/MYSQL_WORKBENCH_EXECUTION_GUIDE.md](docs/MYSQL_WORKBENCH_EXECUTION_GUIDE.md) for inspection, reset and faculty-demonstration steps.

## Python setup on Windows

Clone the repository and enter the project directory:

```powershell
git clone https://github.com/DevenGaikwad/MatCount.git
Set-Location MatCount
```

For the release-candidate ZIP, extract into a new directory and run the following commands there. Keep the separately verified original v2 ZIP intact; do not extract over existing private configuration.

In the VS Code terminal, from this repository:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Set-Location frontend
npm ci
Set-Location ..
```

If PowerShell blocks activation for the current terminal only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Configuration and demonstration credentials

1. Copy `.env.example` to `.env`, or copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`.
2. Keep `DB_NAME=sems_db` so Workbench and Streamlit access the same database.
3. Use a dedicated `sems_app` MySQL account; do not run the application permanently as root.
4. Generate a local bcrypt hash:

   ```powershell
   python scripts/generate_demo_hash.py
   ```

5. Place hashes in protected local configuration and map them to seeded USER emails such as `admin@sems.local`.

Copy private values from an earlier local installation **manually** into fresh ignored configuration after extraction; never carry `.env`, `.streamlit/secrets.toml`, `frontend/.env.local` or real credentials into a commit. Create `sems_db` through the Workbench scripts above; build a *separate* `sems_test` only for integration tests using the guarded instructions below.

Never commit `.env`, `.streamlit/secrets.toml`, plaintext passwords or actual credential hashes intended to remain private.

## Run the professional application

Start the API in terminal 1 from the project root:

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

Start Next.js in terminal 2:

```powershell
Set-Location frontend
npm run dev
```

Open `http://127.0.0.1:3000`. The browser receives only the non-sensitive API address from `NEXT_PUBLIC_SEMS_API_URL`; database credentials remain in the Python process.

The preserved fallback remains available until final parity approval:

```powershell
streamlit run app.py
```

Both interfaces use the same service/repository stack and `sems_db`. Workbench does not need to remain open.

## Tests

Canonical Windows acceptance after local configuration:

```powershell
.\scripts\final_acceptance.ps1
```

This non-destructive orchestrator checks structure/runtimes, Python and SQL contracts, live `sems_db`, the dedicated `_test` guard, full pytest/API checks, frontend type-check/lint/Vitest/production build and secret hygiene. It does not rebuild or reseed `sems_db`.

Server-independent validation during development:

```powershell
python scripts/validate_project.py
```

Local readiness/DB health before a demonstration:

```powershell
python scripts/preflight_check.py
python scripts/validate_project.py --local-acceptance
```

Server-independent tests:

```powershell
pytest -m "not integration"
```

Full suite with a separately built test database:

```powershell
$env:DB_PASSWORD = "YOUR_LOCAL_TEST_ADMIN_PASSWORD"
python scripts/build_database.py --database sems_test --user root
$env:SEMS_TEST_DATABASE_URL = "mysql+pymysql://root:YOUR_URL_ENCODED_PASSWORD@127.0.0.1:3306/sems_test?charset=utf8mb4"
pytest
```

Never point integration tests at valued production/demo data. The test fixture rejects database names that do not end in `_test`.

## Recorded v2 validation status (2026-08-24)

- Current static SQL/academic contract: passed for nine SQL/support scripts, three original demos, 13 ETCS302 SQL demos, optional NoSQL evidence, 13 production relations and seven views.
- Current Python compile and AST parse: PASS.
- Current server-independent Python/API suite: **131 passed, 20 MySQL-only cases deselected**, 0 failed.
- Current broad sandbox pytest run: **131 passed, 20 skipped**, 0 failed; the skipped cases require a safely configured MySQL `_test` database.
- Dedicated API suite: **17 passed**; focused data-policy/service/API security suite: **30 passed**.
- Frontend: strict TypeScript PASS; ESLint PASS with zero warnings; Vitest **10 passed**; optimized Next.js production build PASS for 14 routes; production-server startup PASS.
- Secret hygiene and API-layer boundary scans: PASS.
- Verified v2 source archive: ZIP readability and SHA-256 PASS; an extracted-copy test/build passed in the recorded v2 package validation.
- Python dependency consistency: PASS in the recorded August v2 validation. The original package's later npm audit failed, which prompted the separate patched candidate below.
- Actual MySQL 8.4.11/Workbench execution: **not performed in this environment** because no MySQL server/client is installed.
- Browser-rendered/human visual acceptance and screenshots: not fabricated; this sandbox has no browser executable, so complete them after genuine local execution.

The historical local **118 passed / 0 failed** and MySQL 8.4.11 evidence predates this modernization and remains reference evidence only. A fresh Windows/MySQL run of `final_acceptance.ps1` is required before declaring final academic release.

These are the v2 package's recorded validation results, **not a new Windows/MySQL run in this publication environment**. See [project state](docs/PROJECT_STATE.md) and [validation report](docs/VALIDATION_REPORT.md) for the checkpoint. Before final declaration, run the acceptance command again from a clean extraction on the intended machine.

## Patched-candidate checks (2026-10-04)

| Check | Fresh result here | Limit |
|---|---|---|
| SQL contract and ETCS302 demonstrations | 13 relations, seven views, 13 SQL scripts | Static source check, not live MySQL |
| Python/API | 131 passed, 20 MySQL cases deselected; API 17 passed; focused security 30 passed | No `sems_test` server here |
| Python dependency and secret checks | `pip check` PASS; scanner PASS | No live private configuration |
| Frontend | TypeScript PASS; ESLint zero warnings; Vitest 10 passed; official Webpack build PASS, 14 generated pages | Browser/role visual proof pending |
| npm runtime audit | Zero findings | Registry snapshot at audit time |
| Full npm audit | Five high affected development packages, all in one unfixed `braces` advisory chain | Explicit, narrow CI exception; revisit when patched |
| Original v2 archive | SHA-256 and ZIP integrity PASS, unchanged | Historical source; do not present it as the patched release |

The default Turbopack build attempted here could not bind its CSS worker process in this sandbox. The supported Next.js `--webpack` build completed successfully and is the committed production-build command. The Windows/MySQL/Workbench acceptance and genuine browser screenshots remain pending.

## Verify the original v2 release archive

The archival asset `SEMS_Final_Academic_Professional_Release_v2.zip` must hash to:

```text
bf7c69e72a03ee50296ea1cdaa45764317b93676712866c38885fb47ebff60b0
```

The original ZIP is retained privately for provenance. The patched MatCount candidate has its **own** archive and checksum; never represent changed bytes with the original digest. To verify the original local archive and companion checksum in PowerShell:

```powershell
(Get-FileHash .\SEMS_Final_Academic_Professional_Release_v2.zip -Algorithm SHA256).Hash.ToLower()
Get-Content .\SEMS_Final_Academic_Professional_Release_v2.zip.sha256
```

On Linux/macOS, run `sha256sum SEMS_Final_Academic_Professional_Release_v2.zip` and compare the digest to both the manifest and the value above. Stop if any value differs. See [release/README.md](release/README.md) for the new candidate asset and post-download verification procedure.

## Repository map

```text
frontend/               Canonical Next.js/React/TypeScript/Tailwind interface
api/                    Thin FastAPI authentication and HTTP adapters
app.py, pages/, ui/      Preserved Streamlit fallback
services/               RBAC, validation, workflow and transactions
repositories/           Persistence/query-only layer
db/                     SQLAlchemy models, engine, sessions and healthcheck
config/                 Settings, constants and logging
sql/                    Workbench build, verification and guarded reset scripts
academic_demo/          Safety-labelled ETCS302 SQL and optional NoSQL teaching evidence
tests/                  Unit, contract, architecture and MySQL integration tests
scripts/                Build, static checks, secret scan and final acceptance
docs/                   Frozen baseline and implementation documentation
.github/workflows/       Server-independent CI and publication-integrity checks
release/                 Original archive checksum and verification instructions
```

## Safety boundaries

- Exactly 13 frozen relations; no `password_hash`, `destination_inventory_id`, `lab_status` or audit table.
- Approval transfers Q from available to reserved.
- Pre-dispatch cancellation releases Q.
- Dispatch reduces reserved only.
- Receipt and return require an explicitly selected destination inventory/location.
- Lifecycle records are preserved through states rather than casual deletion.

## Academic DBMS concepts demonstrated

DDL/DML/DCL/TCL, candidate/primary/foreign keys, composite keys, UNIQUE/NOT NULL/DEFAULT/CHECK, AUTO_INCREMENT, normalized multivalued and associative relations, relational algebra/set operations, joins/subqueries/aggregates/CTEs/window functions, seven views, justified indexes with EXPLAIN/EXPLAIN ANALYZE, procedures/functions, triggers, a cursor, savepoints, concurrency/deadlock/recovery, application RBAC and an optional NoSQL/CAP extension. See `docs/ETCS302_SYLLABUS_TRACEABILITY_MATRIX.md` and `docs/DBMS_ACADEMIC_COVERAGE_REPORT.md`.

## Screenshot placeholders

No evidence image is bundled or fabricated. After genuine local acceptance, capture the numbered evidence in `docs/SCREENSHOT_EVIDENCE_PLAN.md` (MySQL version/schema, constraints/JOIN/view, acceptance output, professional login/dashboard/workflows and Next.js → FastAPI → MySQL persistence proof in Workbench).

The [screenshot intake](docs/screenshots/README.md) keeps every slot explicitly pending. Only genuine, sanitized command-prompt, Workbench and browser screenshots may be submitted; never show passwords, tokens, hashes, private configuration, desktop notifications or unrelated personal data.

## Faculty demonstration path

In Workbench confirm `SELECT VERSION()` and `SELECT DATABASE()`, count the 13 base relations and seven views, inspect an actual PK/FK and execute `sql/07_verification_queries.sql`. Run one meaningful JOIN, then a documented safe constraint/rollback demonstration in the isolated academic schema. Start FastAPI and Next.js, sign in with configured demonstration roles, perform an authorized inventory/request/transfer action and prove its persisted result with a Workbench `SELECT` on the same `sems_db`. Finish with the actual `final_acceptance.ps1` summary. Follow the exact [faculty guide](docs/FACULTY_DEMO_GUIDE.md); screenshots stay pending until captured.

## Security, accessibility and reuse

Student financial-data restrictions and CSV minimization are enforced in Python service/API responses, not only by hiding fields in React. Sessions, active-user checks, role and lab scope remain server-side; demonstrations must use synthetic data and private configuration. Report suspected vulnerabilities privately using [SECURITY.md](SECURITY.md), never in a public issue. Dialog and keyboard handling follow [WAI-ARIA modal-dialog guidance](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) and [WCAG 2.2 focus-visible guidance](https://www.w3.org/WAI/WCAG22/Understanding/focus-visible/); this is not a claim of formal accessibility certification.

No open-source licence has currently been granted. The source is published for academic review and demonstration. Reuse, redistribution, or derivative use requires permission from the project authors unless otherwise stated for third-party components.

## Known limitations and future scope

The frozen MVP does not persist destination inventory on TRANSFER_ITEM, stores demo hashes outside USER, has no LAB activation attribute, returns complete temporary lines, and cannot preserve historical disposal unit cost independently of current INVENTORY cost. See `docs/known_issues.md`.

Future scope—not current MVP—includes procurement, maintenance, serialization, QR/barcodes, audit-log tables, notifications, AI/compatibility recommendations, IoT, predictive features and remote deployment.

**Release status:** The source package is complete. Final academic-release status requires successful fresh execution on the intended Windows, MySQL 8.4.11, and MySQL Workbench environment, followed by role-workflow and genuine visual acceptance.
