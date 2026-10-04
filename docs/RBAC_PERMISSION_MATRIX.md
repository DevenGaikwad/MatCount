# SEMS Role-Based Permission and Data-Minimization Matrix

**Authority:** frozen role semantics plus current service/API enforcement  
**Security principle:** navigation is convenience; FastAPI dependency, service role checks, lab scope, active-account revalidation and response projection are the security boundary.

## Data visibility policy

| Data class | Student | Faculty | Lab Assistant | Administrator |
|---|---|---|---|---|
| Component catalogue | Read | Read | Read | Read/manage |
| Permitted availability | Cross-lab summarized | Cross-lab operational | Own-lab operational | Global operational |
| Cabinet/shelf/drawer in availability response | No | Yes | Own lab | Global |
| Raw INVENTORY positions | No | No | Own lab | Global |
| Unit cost / valuation | **No** | **No** | Own-lab duties | Global |
| Other-user directory/phones | No | No | No | Manage |
| Own request and progress | Yes | Own/own-lab as appropriate | Own-lab operational queue | Global |
| Transfer details | No | Relevant lab monitoring | Relevant operational scope | Global |
| Disposal history/control | No | No | No | Global |
| CSV financial fields | **No** | **No** | Role/lab-scoped | Global |

`services/data_policy.py` removes `unit_cost`, `available_value`, `inventory_value`, `inventory_valuation`, `disposed_value` and `total_on_hand_inventory_value` before unauthorized API serialization or CSV generation. Student availability is an allowlisted projection that also excludes storage coordinates, reserved/accounted quantities and administrative detail.

## CRUD and workflow capability matrix

Legend: **G** global, **L** assigned/relevant laboratory, **O** own record, **R** read, **C/U** create/update, **—** denied.

| Capability | Student | Faculty | Lab Assistant | Administrator | Enforcement authority |
|---|---:|---:|---:|---:|---|
| Authenticate / end own session | O | O | O | O | auth route + opaque session store |
| Dashboard | O/L | L | L | G | analytics scope + financial projection |
| Labs read | R | R | R | R | authenticated API |
| Labs/contact manage | — | — | — | C/U G | `master_data_service` |
| Users/phones read/manage | — | — | — | R/C/U G | `master_data_service` |
| Categories/components read | R | R | R | R | authenticated API |
| Categories/components manage | — | — | — | C/U G | `master_data_service` |
| Storage locations | — | — | R/C/U L | R/C/U G | `master_data_service` + lab scope |
| Availability browse | R minimized | R no finance | R L + finance | R G + finance | `analytics_service` + data policy |
| Raw inventory/create/restock/metadata/status | — | — | R/C/U L | R/C/U G | `inventory_service` + row locks |
| Request create/submit/cancel | C/U O,L | C/U O,L | — | C/U G | `request_service` creator/lab checks |
| Request read | O | L | L/approved stock-planning context | G | `request_service` |
| Request review approve/reject quantities | — | U L | — | U G | `request_service.review_request` |
| Transfer monitor | — | R L | R relevant | R G | `transfer_service` scope |
| Transfer plan/cancel before dispatch | — | — | C/U source L | C/U G | `transfer_service` |
| Transfer approve/reject | — | — | — | U G | Administrator role check |
| Dispatch | — | — | U source L | U G | source scope + locked inventory |
| Receive | — | — | U destination L | U G | destination scope + selected position |
| Return temporary lines | — | — | U relevant L | U G | relevant-lab scope + locks |
| Disposal read/create | — | — | — | R/C G | `disposal_service` |
| Permitted reports/export | O/minimized | L/no finance | L/operational | G/all | report allowlist, scope, projection, CSV safety |
| Physical DELETE of lifecycle rows | — | — | — | — | deliberately absent from UI/API |

## Page and API boundary

| Page/API family | Student | Faculty | Lab Assistant | Administrator |
|---|---:|---:|---:|---:|
| `/dashboard`, `/components`, `/inventory`, `/requests`, `/reports` | Visible | Visible | Visible | Visible |
| `/transfers` | Hidden / API denied | Visible monitor | Visible operate | Visible approve/operate |
| `/storage-locations` | Hidden / API denied | Hidden / API denied | Visible own lab | Visible global |
| `/laboratories`, `/users` | Hidden for management | Hidden for management | Hidden for management | Visible |
| `/disposal` | Hidden / API denied | Hidden / API denied | Hidden / API denied | Visible |

The laboratory catalogue remains authenticated-readable because lab names are required for availability/request context; contacts and user records are Administrator-only.

## Controls and evidence

- `current_actor` rejects missing/expired opaque bearer sessions.
- `revalidate_actor` detects suspended/deactivated users and stale role, email or lab identity.
- `require_roles`, `require_lab_scope` and `require_any_lab_scope` execute inside services, not only routes.
- SQLAlchemy bound parameters and fixed report-view allowlists protect query construction.
- request bodies use strict Pydantic bounds; service validation repeats domain-critical rules.
- CSV output neutralizes spreadsheet formula prefixes.
- `tests/test_data_policy.py` proves financial removal and export minimization.
- `tests/test_service_security.py` proves direct service bypass attempts fail.
- `tests/api/test_api_contract.py` proves direct unauthorized API calls return 403 and Student inventory responses contain no financial/storage fields.
- `frontend/lib/permissions.test.ts` proves visible navigation/capabilities align with the documented policy, but frontend hiding is never treated as authorization.

## Explicit policy decisions

1. Faculty can review own-lab request quantities but has no financial visibility and cannot approve or execute transfers.
2. Lab Assistants need own-lab cost for stock duties but cannot enumerate users, authorize disposal or approve transfers.
3. Administrators represent department-wide/HOD-equivalent oversight.
4. Student availability is intentionally useful but minimal: component, laboratory, free quantity and status; no coordinates, reservations or value.
5. No role can casually delete lifecycle history through the application.

