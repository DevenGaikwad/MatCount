# SEMS Workflows and Transaction Rules

## Authentication

1. Verify a local bcrypt demo hash outside the schema.
2. Map authenticated email to ``USER.email``.
3. Require `account_status=ACTIVE`.
4. Load role and lab scope into a session Actor.
5. Recheck the Actor against USER on active app/session operations; role/lab/status changes require sign-in again.

## Inventory

### Registration/restock

1. Lab Assistant or Administrator selects a lab, component and location.
2. Service verifies role/lab scope and location ownership.
3. Service performs null/quantity/cost validation.
4. Database UNIQUE/FK/CHECK and same-lab trigger protections apply.
5. Status is derived from free quantity and component minimum stock unless manually BLOCKED/INACTIVE.

### Quantity meanings

```text
available = physical stock free for allocation
reserved  = approved stock not yet dispatched
```

## Component requests

```text
Request header:
DRAFT → SUBMITTED → PARTIALLY_APPROVED / APPROVED / REJECTED
PARTIALLY_APPROVED or APPROVED → FULFILLED after all approved lines are fulfilled
DRAFT → CANCELLED
SUBMITTED → CANCELLED before approval/allocation

Request item:
PENDING → PARTIALLY_APPROVED / APPROVED / REJECTED → ALLOCATED → FULFILLED
```

1. Student, Faculty or Administrator creates a DRAFT with unique component lines.
2. Submission requires at least one positive-quantity line.
3. Faculty/Administrator reviews every line atomically; approval quantities become immutable after transfer allocation starts.
4. Approved quantity must remain between zero and requested quantity.
5. Header status is derived from line statuses; it is not manually contradicted.

## Inter-laboratory transfer

### Plan

1. Lab Assistant/Administrator selects an approved request.
2. Destination must equal the requesting lab; source must differ.
3. Source inventory allocations must match approved components and remaining quantities.
4. Transfer begins as DRAFT/PENDING with one or more TRANSFER_ITEM rows.

### Approve/reserve

1. Administrator locks the header, lines and all source inventories.
2. Inventory locks are acquired in ascending `inventory_id` order.
3. Free stock is rechecked.
4. For quantity Q: `available -= Q`; `reserved += Q`.
5. Header becomes APPROVED/APPROVED and request progress is recomputed.
6. Any failure rolls back the entire multi-item operation.

### Cancel before dispatch

- DRAFT cancellation changes status only.
- APPROVED cancellation releases each exact Q: `available += Q`; `reserved -= Q`.
- Cancellation after dispatch is rejected.

### Dispatch

1. Source Lab Assistant/Administrator confirms every item condition.
2. Lock and recheck source rows.
3. `reserved -= quantity_sent` only; no second available subtraction.
4. Store `condition_on_issue`, dispatch date and DISPATCHED state atomically.

### Receipt

1. Destination Lab Assistant/Administrator explicitly selects an existing destination inventory or destination location for each item.
2. Service validates destination lab, component and storage ownership.
3. Existing source/destination rows are locked in stable ID order; a missing destination position is created safely.
4. Add only the newly received delta to destination available stock.
5. A transfer becomes RECEIVED and records receiver/date only after all item totals equal quantities sent.
6. No destination inventory ID is stored in TRANSFER_ITEM.
7. While any cumulative line is incomplete, the transfer remains DISPATCHED because the frozen state domain has no PARTIALLY_RECEIVED value.

### Temporary return

1. A non-NULL return due date marks a temporary line.
2. Operator explicitly selects the current destination inventory.
3. Lock destination and original source rows in stable order.
4. For a complete returned line: destination available decreases; source available increases.
5. Store actual return date and `condition_on_return`.
6. Header is PARTIALLY_RETURNED while another temporary line remains; otherwise RETURNED.

## Disposal

1. Administrator selects free inventory and enters positive quantity, date, reason and method.
2. Service locks the inventory row and rechecks available stock.
3. Insert DISPOSAL_RECORD and decrement available quantity in one transaction.
4. Reserved stock cannot be disposed.
5. Disposal history is retained; no casual lifecycle deletion is exposed.

## Reporting

- SQL views define stable grains.
- Non-administrator dashboards/reports are lab-scoped, while the availability search supports cross-lab discovery.
- CSV export is mandatory.
- Formula-like text cells are apostrophe-neutralized before CSV download; numeric values are unchanged.
- Empty result sets render informative messages rather than fabricated data.
