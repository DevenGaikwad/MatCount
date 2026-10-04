# SEMS User Manual

## Purpose

SEMS provides centralized component visibility and controlled laboratory workflows while preserving laboratory ownership, approvals and stock history. The application connects to the same `sems_db` that can be inspected in MySQL Workbench.

## Start and sign in

1. Confirm MySQL Server is running and `sems_db` has been built.
2. From the activated Python environment, start the API:

   ```powershell
   python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
   ```

3. In a second terminal, run `Set-Location frontend` and `npm run dev`, then open `http://127.0.0.1:3000`.
4. Sign in with an externally configured demonstration credential. The email must match an ACTIVE seeded `USER`; no password is stored in the database or frontend.
5. If the database health check fails, stop and correct the Python/MySQL connection settings. Do not continue with assumed or offline data.

The browser talks only to FastAPI. FastAPI delegates to the same service/repository stack as the preserved Streamlit fallback, and both use the same `sems_db` shown in Workbench.

## Roles and visible work

| Role | Main permitted work |
|---|---|
| Student | Search cross-laboratory availability; create and submit own-lab component requests; inspect request progress |
| Faculty | Student capabilities plus review/approve/reject request quantities for the permitted laboratory and monitor relevant transfers; no transfer approval/execution |
| Lab Assistant | Manage own-lab storage/inventory; plan allocations; dispatch, receive and return transfers within the applicable source/destination scope |
| Administrator | Manage all laboratories/master data; approve/reject transfers; perform controlled workflows; authorize disposal; view system-wide analytics |

Navigation is filtered for usability, but every actor-aware service call is independently checked. Existing sessions are invalidated if database email, role, lab or status changes; inactive/suspended accounts are denied.

Financial visibility is deliberately narrower than page visibility. Students and Faculty receive no unit-cost or valuation fields from the API or CSV. Student availability also excludes storage coordinates and reserved/accounted quantities. Lab Assistants may use cost only for own-laboratory stock duties; Administrators have department-wide valuation. A missing UI column is not the protection—the server response is minimized.

## Page guide

| Page | Use |
|---|---|
| Dashboard | Review role-scoped KPIs, stock-by-lab and request-status visuals |
| Laboratories | Maintain laboratory and contact details within administrator permissions |
| Users | Maintain users, roles, account states and normalized phone numbers |
| Component Catalogue | Maintain categories and reusable component definitions |
| Storage Locations | Maintain laboratory-owned room/cabinet/shelf/drawer coordinates |
| Inventory | Search availability; register, restock, move and control stock rows |
| Component Requests | Create multi-line requests, submit them and perform line-by-line review |
| Transfers | Inspect a visual lifecycle; plan approved demand, reserve, dispatch, receive and return stock through dedicated dialogs |
| Disposal | Review history/impact metrics and record administrator-authorized retirement after typing explicit confirmation |
| Reports | Select a documented SQL-view grain, inspect a focused chart/table and download formula-safe CSV |

Shared data tables support search, sortable headings, paging, column visibility and comfortable/compact density. Wide tables scroll inside their panel. Use the **Columns** menu to restore a hidden field; role-prohibited fields are not offered because they are absent from the API response.

## Core task procedures

### Search component availability

1. Open **Inventory** from the role-aware sidebar.
2. Search by component, category, part number or laboratory.
3. Read `quantity_available` as unallocated stock. Reserved quantity/location/value appears only when your role is permitted to receive it.
4. Search results may span laboratories; modification controls remain role/lab scoped.

### Create and submit a component request

1. Open **Component Requests** and create a DRAFT for the permitted requesting laboratory.
2. Add each component once with a positive requested quantity.
3. Review all lines, then submit. An empty request cannot be submitted.
4. Faculty/Administrator reviews every line. The approved quantity cannot exceed the requested quantity.
5. Header progress is derived from line outcomes; do not infer approval from one line alone.

### Plan and approve a transfer

1. Open **Transfers** and choose **Plan Transfer**. Only Lab Assistant/Administrator sees the operational control.
2. Choose a source laboratory different from the request destination.
3. Allocate source inventory rows whose component and remaining quantities match the approved request lines. The dedicated planning read does not grant ordinary access to another laboratory's request history.
4. Administrator approves the transfer. For each quantity `Q`, approval atomically applies:

   ```text
   quantity_available -= Q
   quantity_reserved  += Q
   ```

5. Cancelling an approved transfer before dispatch releases the exact reservation.

### Dispatch and receive

1. Source Lab Assistant/Administrator records `condition_on_issue` and dispatches.
2. Dispatch subtracts from reserved stock only; available stock was already reduced at approval.
3. At receipt, the destination operator explicitly selects either an existing destination inventory row or a validated destination storage location.
4. Confirm each item. SEMS adds only the newly received delta to destination available stock.
5. If any line is incomplete, the header remains DISPATCHED; a later confirmation uses cumulative quantities and cannot increment the same quantity twice.
6. `TRANSFER_ITEM` intentionally retains only its source inventory FK; the runtime destination choice is not added to the frozen schema.

### Return temporary stock

1. A transfer item is temporary when it has a return due date.
2. Select the current destination inventory explicitly.
3. Return a complete temporary line: destination available decreases and original source available increases.
4. Record the actual return date and `condition_on_return`.
5. A multi-line transfer remains PARTIALLY_RETURNED until all temporary lines are returned.

### Record a disposal

1. Administrator opens **Disposal** and selects an inventory row.
2. Enter a positive quantity, disposal date, reason and method.
3. Review the calculated before/after quantity and estimated value, then type `DISPOSE` and confirm. The record insertion and available-stock decrement occur in one transaction.
4. Reserved stock cannot be disposed, and disposal history is retained.

### Export a report

1. Open **Reports** and select one of the role-permitted report cards.
2. Apply any available filters.
3. Confirm the displayed grain before interpreting totals.
4. Download CSV. Empty reports show an informative state and do not invent data. Formula-like text is prefixed with an apostrophe to reduce spreadsheet formula-injection risk; numeric values remain numeric.

## Safe demonstration sequence

1. Log in as Administrator and show dashboard/master data.
2. Log in as Student and search availability/create a request.
3. Log in as Faculty and partially approve request quantities.
4. Log in as Lab Assistant to plan an allocation; log in as Administrator to approve/reserve it; then use Lab Assistant to dispatch.
5. Receive into an explicit destination and show updated reports.
6. Return to Workbench and run a corresponding SELECT from `07_verification_queries.sql` to prove the browser → FastAPI → service → SQLAlchemy → MySQL write persisted.

Use only locally configured demonstration passwords. Do not display real secrets in screenshots or viva materials.

## Fallback and session behavior

- Streamlit remains available with `streamlit run app.py` until the user approves final parity; it must not be deleted during acceptance.
- The modern API session is intentionally process-local. Restarting Uvicorn signs users out; this is expected for the single-machine academic target.
- The frontend keeps only an opaque token in the current browser tab/session. A role, lab, email or account-status change in MySQL invalidates subsequent operations and requires a fresh login.

## Common messages

| Message | Meaning/action |
|---|---|
| Database unavailable | Start MySQL and verify host, port, user, password and `DB_NAME=sems_db` |
| Permission denied | Use the correct role/lab or ask the administrator; hiding a page is not an authorization grant |
| Insufficient free stock | Reduce allocation or restock; reserved quantity is not free stock |
| Invalid destination | Select storage/inventory owned by the transfer destination laboratory and matching the component |
| Duplicate line/location | Reuse/update the existing logical row; SEMS prevents duplicate component lines and null-normalized storage coordinates |
