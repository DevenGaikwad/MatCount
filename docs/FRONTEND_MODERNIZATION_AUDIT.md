# SEMS Current Implementation and Frontend Modernization Audit

> **Historical modernization decision audit.** The current premium/ETCS302 A–AF audit is `PREMIUM_UI_ETCS302_GAP_AUDIT.md`.

**Audit date:** 2026-08-23  
**Database baseline:** SEMS v1.0 — exactly 13 frozen relations  
**Rollback checkpoint:** `SEMS_Release_Candidate.zip` (preserved outside the working tree)  
**Verified pre-modernization local baseline supplied by the user:** MySQL 8.4.11, `sems_db`, `sems_test`, 118 passed/0 failed, local acceptance 5/5

## A. Current codebase/artifact detected

The working tree is the maximum-quality SEMS release candidate. It contains the Streamlit application, ten pages, Python services/repositories, SQLAlchemy mappings, MySQL scripts, 94 test functions (118 collected cases in the verified Windows run), and the complete academic documentation set. The older Phase 2–12 package is not the active source.

## B. Current backend architecture

The backend already follows the correct path:

`Streamlit page → service → repository → SQLAlchemy → PyMySQL → MySQL 8.4.11 / sems_db`

Services own validation, authorization, workflow changes and transaction boundaries. Repositories own persistence/query access. Stock-changing operations use the established transaction and row-locking rules. This backend is protected and will be reused, not rewritten.

## C. Current Streamlit architecture

- `app.py` owns login, session revalidation and role-aware `st.navigation`.
- `pages/01`–`10` provide dashboard, masters, inventory, requests, transfers, disposal and reports.
- `ui/session.py` stores the actor in Streamlit session state.
- `ui/components.py` provides headers, KPIs, tables, error display and CSV download.
- `ui/theme.py` injects the DESPU-inspired CSS layer.

## D. Current shared UI/theme

The current theme correctly establishes orange, amber, warm-white, maroon, charcoal and muted-text tokens. It improves cards, headers, buttons, focus and responsive spacing. It is, however, an injected stylesheet over framework-owned markup rather than a complete component/design system.

## E. Authentication/session

Authentication is external to the frozen `USER` table. Bcrypt hashes remain in protected configuration, verified email maps to `USER.email`, and the database actor is revalidated for role, laboratory and account status. The new web boundary must retain these rules server-side.

## F. API availability

No HTTP API currently exists. Streamlit imports services directly. A thin FastAPI adapter is therefore required for a standalone browser frontend; it must call existing services and must never expose repositories or MySQL directly.

## G. Module-by-module frontend state

| Module | Current state | Modernization need |
|---|---|---|
| Login | Functional centered form; technical health alert | Branded split layout, discreet status, show/hide password, clean unauthenticated shell |
| Dashboard | Accurate KPI cards and two Plotly charts | Professional grid, role-scoped operational panels, responsive chart cards |
| Laboratories | Search/table plus stacked create/contact/update forms | Searchable grid, focused modal/drawer forms, detail contacts |
| Users | Correct external-credential notice and CRUD | Role/status chips, lab names, structured forms and phone detail |
| Catalogue | Search/category filter and administrator tabs | Polished searchable catalogue and coherent category/component actions |
| Storage | Correct lab scope/null-normalized rules | Location labels, filters, compact create/edit dialogs |
| Inventory | Strongest operational semantics; generic table/forms | Flagship data grid, human labels, status/value formatting and safe action dialogs |
| Requests | Complete multi-line lifecycle | Request cards/table, detail drawer, line-item builder and review workspace |
| Transfers | Complete but long 411-line page | Dedicated lifecycle workspace, timeline, item tables and stage-specific actions |
| Disposal | Correct administrator-only atomic action | Deliberate danger/confirmation UX and clearer inventory context |
| Reports | Seven views and CSV | Report catalogue, descriptions, filters, table/chart panels and stable download |

## H. Why the current interface looks basic

The UI is constrained by Streamlit's generated DOM, fixed widget composition, rerun model, generic dataframe presentation, emoji navigation and long vertically stacked forms. Achieving a premium shell, drawers, reusable data grids, responsive interaction states and a coherent workflow timeline would require brittle CSS/DOM targeting.

## I–K. Decision and technical reasoning

**Decision: migrate the canonical presentation layer to Next.js + React + TypeScript + Tailwind CSS, while retaining Streamlit as the known-good fallback.**

This provides semantic components, accessible dialogs, a true authenticated shell, route-level organization, typed API contracts, maintainable responsive grids and production-build validation. It introduces one explainable transport layer but does not change the database, repositories, services or workflow semantics.

## L. Proposed architecture

`Browser → Next.js/React/TypeScript/Tailwind → HTTP/JSON → thin FastAPI routes → existing Python services → repositories → SQLAlchemy → PyMySQL → MySQL 8.4.11 / sems_db`

The Node frontend never connects to MySQL. Service-level RBAC remains authoritative. API sessions are opaque, server-held and short-lived; credential hashes never enter browser code.

## M. Files/directories to add

- `api/`: application, dependencies, session store, schemas, serializers and service-facing routes.
- `frontend/`: Next.js App Router application, reusable components, features, API client, types and design tokens.
- `tests/api/`: focused HTTP-boundary tests.
- `scripts/final_acceptance.ps1`: Windows-first non-destructive acceptance orchestration.

## N. Files/directories to preserve

`app.py`, `pages/`, `ui/`, `services/`, `repositories/`, `db/`, `sql/`, current tests and all frozen academic documents remain present. Streamlit continues to be runnable as the reference interface during acceptance.

## O. Protected files/semantics

The 13-table DDL, ORM table/column mappings, PK/FK directions, relationship cardinalities, stock equations, request/transfer state domains, external authentication decision and service transaction semantics must not change for presentation convenience.

## P. Main regression risks

1. Bypassing services from API routes.
2. Trusting frontend role/lab claims.
3. Exposing credentials or hashes to the client.
4. Payload/date/decimal conversion drift.
5. Different role visibility from service authorization.
6. Stale session actors after USER changes.
7. Frontend action labels implying unsupported state changes.

## Q. Implementation sequence

1. Preserve the existing ZIP checkpoint and freeze backend boundaries.
2. Add generic safe serialization and opaque API sessions.
3. Expose read operations, then mutation routes mapped one-to-one to services.
4. Build the design system and authentication shell.
5. Migrate dashboard, masters, inventory, requests, transfers, disposal and reports.
6. Add focused API/frontend checks and production build validation.
7. Add the PowerShell acceptance orchestrator.
8. Synchronize documentation and prepare a clean professional release candidate.

## R. Testing strategy

- Preserve the verified 118-case Python baseline as historical pre-modernization evidence.
- Run fresh Python compile, SQL contract, architecture and pytest checks where dependencies exist.
- Add API authentication/RBAC/error-contract tests without duplicating every service test.
- Run TypeScript, ESLint, focused frontend tests and `next build`.
- Keep MySQL integration restricted to `sems_test` and rerun full Windows acceptance after handoff.

## S. `final_acceptance.ps1` plan

The orchestrator will validate structure/runtimes, reuse `validate_project.py --local-acceptance`, enforce `_test` safety, run the complete Python suite, validate the API, inspect actual frontend scripts, run type-check/lint/tests/build, scan for secret leakage, write a sanitized local evidence log and return a non-zero exit code on mandatory failure. It will never rebuild or drop `sems_db`.
