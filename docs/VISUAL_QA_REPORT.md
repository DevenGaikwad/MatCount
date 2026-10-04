# SEMS Premium Frontend Visual QA Report

**Date:** 2026-08-24  
**Scope:** login plus ten authenticated routes, desktop/tablet/mobile behavior and core dialogs/tables  
**Acceptance state:** source/build/static-responsive review complete; rendered-browser and human visual acceptance pending local execution.

## Evidence completed in this environment

- Next.js optimized production build generated all 14 static routes successfully.
- strict TypeScript, ESLint and Vitest checks passed after the design-system/RBAC refinements.
- every major route component was inspected for shared shell, PageHeader, Panel, DataTable, dialog/form and empty/loading/error-state usage.
- CSS breakpoints and overflow containment were inspected at the declared 1180, 900 and 620 px thresholds.
- accessibility source checks confirmed visible `:focus-visible`, labelled modal dialog, focus trap/restoration, Escape close, body scroll lock, keyboard table-row activation, table caption/`aria-sort`, `aria-current`, reduced-motion behavior and labelled mobile navigation controls.
- a local Next.js production server started successfully at `127.0.0.1:3000`.

## Rendered-browser limitation

An automated Playwright route/screenshot harness was prepared for 1366×768, 1920×1080, 1024×768 and 390×844 with mocked non-production API data. It could not run because this sandbox contains the Playwright library but no Chromium/Firefox/WebKit executable, and downloading a browser is not authorized/available. No screenshot was fabricated or substituted.

Therefore this release is described as **premium UI source complete**, not visually accepted. The generated QA harness and mock screenshots are not included in the release archive. Final visual acceptance must use the actual Windows application and real role-scoped data.

## Source-level route checklist

| Route | Primary quality checks | Source status | Rendered local status |
|---|---|---|---|
| Login | institutional split layout, safe health wording, password toggle, validation/focus, no demo secret | reviewed | pending |
| Dashboard | role-specific hero, four primary KPIs, quick actions, operational pulse, real-data charts | reviewed | pending all roles |
| Laboratories | readable master table, selection/detail, contact dialog | reviewed | pending |
| Users | private Admin-only directory, role/status context, phone workflow | reviewed | pending |
| Component Catalogue | category/component hierarchy, searchable table, edit forms | reviewed | pending |
| Storage Locations | lab scoping, coordinate table, responsive form | reviewed | pending |
| Inventory | role-specific columns and notices, financial minimization, stock controls | reviewed/tested at policy layer | pending all roles |
| Component Requests | multi-line creation, selection/detail, review states/dialog | reviewed | pending Student/Faculty/Admin |
| Transfers | lifecycle timeline, planning/approval/dispatch/receipt/return actions | reviewed | pending Lab Assistant/Admin |
| Disposal | Administrator-only history and guarded form | reviewed | pending |
| Reports | role catalogue, metrics, chart/table and CSV control | reviewed/tested at policy layer | pending all roles |

## Responsive design checks in source

| Width | Intended behavior | Static evidence |
|---|---|---|
| 1920×1080 | centered content up to 1660 px; four-column metrics; stable sidebar/topbar | max-width shell, scalable hero/grid |
| 1366×768 | full sidebar, compact sticky topbar, bounded table/dialog scrolling | 264 px sidebar; table max-height; dialog viewport cap |
| ≤1180 px | three-column metrics; stacked split workspace; adjusted login proportions | first breakpoint |
| ≤900 px | off-canvas sidebar/scrim; two-column metrics; single-column panels; dashboard reflow | tablet breakpoint |
| ≤620 px | single-column metrics/forms/actions; bottom-sheet dialog; stacked toolbar | mobile breakpoint |

Tables deliberately scroll inside `.table-scroll` rather than forcing the whole document wider. Dialog content has its own vertical scroll and a 92vh mobile cap. These are source assurances only until rendered inspection confirms actual content lengths.

## Required local visual acceptance

For each route above:

1. run the real FastAPI and Next.js application;
2. inspect 1366×768 and 1920×1080 in Administrator role;
3. inspect 1024/tablet and 390/mobile widths;
4. repeat the Dashboard, Inventory, Requests and Reports as Student, Faculty and Lab Assistant;
5. open every create/edit/review/workflow dialog and keyboard through it;
6. test long component/lab names, empty/error/loading states, table sorting/search/pagination/column visibility/density;
7. confirm no document-level horizontal overflow, clipped actions, illegible chart label, focus loss or inaccessible modal state;
8. capture only genuine evidence listed in `SCREENSHOT_EVIDENCE_PLAN.md`.

Record actual pass/fail observations in `LOCAL_ACCEPTANCE_CHECKLIST.md`. A failed visual item blocks final academic release but does not authorize schema change.

