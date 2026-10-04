# SEMS Local MySQL 8.4.11 Acceptance Checklist

Record date, machine, MySQL/Python/Node versions and exact commands. Check an item only after observing it; attach genuine evidence IDs from `SCREENSHOT_EVIDENCE_PLAN.md`.

## Canonical automated gate

From the configured project root run:

```powershell
.\scripts\final_acceptance.ps1
```

- [ ] The command completes with `FINAL RESULT: PASS`.
- [ ] `logs/final_acceptance_latest.txt` contains no secret and records current versions/counts.
- [ ] No Python/API/frontend check is failed or silently skipped.
- [ ] npm runtime audit reports zero findings, and the full audit contains no finding outside the precisely documented development-only `braces` exception.
- [ ] All MySQL integration tests execute; they are not merely skipped.
- [ ] The script does not rebuild, reset or reseed `sems_db`.

## A. Environment and database build

- [ ] `python scripts/preflight_check.py` passes.
- [ ] Node.js and npm meet `frontend/package.json` requirements.
- [ ] `SELECT VERSION()` reports **8.4.11**.
- [ ] `SELECT DATABASE()` reports `sems_db` after setup.
- [ ] `sems_db` created from script `00`.
- [ ] Scripts `01`–`06` execute in order without unrecorded errors.
- [ ] Exactly 13 base relations are visible.
- [ ] Exactly seven views are visible.
- [ ] Stored procedure `sp_component_availability` is visible.
- [ ] Function `fn_inventory_available_value` is visible.
- [ ] Both inventory/location triggers are visible.
- [ ] Seed data loaded and representative counts match.
- [ ] `07_verification_queries.sql` passes as read-only verification.

## B. DBMS demonstrations

- [ ] Representative PKs/FKs/UNIQUE/CHECK constraints inspected.
- [ ] One selected EXPECTED FAILURE rejects invalid data without changing valid rows.
- [ ] Transaction demo confirms `rollback_restored_original = 1`.
- [ ] EXPLAIN demo returns plans for all four queries.
- [ ] On-hand valuation includes reserved stock for inventory `5` (`12 × 620`).
- [ ] Partial approval seed request `5` is visible.
- [ ] Overdue temporary return view returns the seeded line at the execution date.
- [ ] Relational-algebra script demonstrates selection/projection/UNION/INTERSECT/EXCEPT/bounded product.
- [ ] Advanced SQL demonstrates INNER/LEFT/RIGHT joins, aggregates/HAVING, correlated queries, EXISTS/NOT EXISTS, CTE and DENSE_RANK.
- [ ] Stored procedure IN/OUT and deterministic function demos execute in the academic schema.
- [ ] Cursor demo shows DECLARE/OPEN/FETCH/NOT FOUND/CLOSE and the set-based alternative.
- [ ] Trigger audit/synchronization teaching tables are visibly under `sems_academic_demo`, not `sems_db`.
- [ ] SAVEPOINT/ROLLBACK TO SAVEPOINT/COMMIT and full ROLLBACK execute in the demo schema.
- [ ] Two-session `FOR UPDATE` demonstration prevents over-allocation.
- [ ] Optional deadlock exercise uses only disposable demo rows; both sessions are rolled back/clean afterward.
- [ ] DCL roles/grants are demonstrated with sanitized local accounts and no password exposure.
- [ ] `sems_db` still contains exactly 13 base relations after all academic demonstrations.

## C. Automated test acceptance

- [ ] Dedicated `sems_test` created; it is not `sems_db`.
- [ ] `SEMS_TEST_DATABASE_URL` ends in `_test`.
- [ ] Server-independent pytest suite executed.
- [ ] All MySQL integration tests executed (not merely skipped).
- [ ] Full pytest exits successfully.
- [ ] Compile/import checks pass.
- [ ] `python scripts/validate_sql_contract.py` passes.
- [ ] `python scripts/validate_project.py --local-acceptance` passes.
- [ ] Exact passed/failed/skipped counts recorded in `VALIDATION_REPORT.md`.

## D. Professional frontend, API and roles

- [ ] FastAPI and Next.js start independently and connect through the configured local API URL.
- [ ] Next.js → FastAPI → Python services accesses the same `sems_db` shown in Workbench.
- [ ] Login works with protected demonstration credentials.
- [ ] Browser storage/network payloads contain no DB password, bcrypt hash or private database URL.
- [ ] API restart invalidates the process-local session cleanly and a new login succeeds.
- [ ] Suspended/inactive user is denied.
- [ ] Student navigation/scope checked: catalogue, availability, own requests; no transfer operations/detail.
- [ ] Student API inventory/dashboard/report/CSV contains zero cost/valuation fields and no storage/reserved/accounted detail.
- [ ] Faculty API/pages contain no cost/valuation fields.
- [ ] Faculty request review checked; Faculty cannot approve/cancel a transfer.
- [ ] Lab Assistant own-lab inventory and operational transfer scope checked.
- [ ] Administrator global masters, transfer approval and disposal checked.
- [ ] Logout and stale-session role/status revalidation checked.
- [ ] Streamlit fallback still starts and remains usable until explicit final-interface approval.

## E. UI/UX and responsive acceptance

- [ ] Login has no authenticated navigation and no demo credential leakage.
- [ ] Sidebar, top bar, role badge, laboratory context and logout are coherent.
- [ ] Dashboard, status badges, loading/error/empty states and feedback are visually consistent.
- [ ] Tables search, sort and paginate without unusable overflow.
- [ ] Forms/dialogs show required fields, safe errors and destructive confirmations.
- [ ] Request and transfer lifecycles are understandable without inspecting code.
- [ ] Reports state their grain and CSV downloads correctly.
- [ ] Keyboard focus is visible and primary controls have meaningful labels.
- [ ] Visual inspection passes at 1366×768 and 1920×1080.
- [ ] Tablet/mobile navigation and forms remain usable.
- [ ] Every route in `VISUAL_QA_REPORT.md` is inspected at the required viewports with actual data.
- [ ] Dialog focus enters, cycles, closes with Escape and returns to its trigger.
- [ ] Table column visibility/density/sort/search/pagination and sticky headers remain usable.
- [ ] Reduced-motion mode and visible keyboard focus are checked.

## F. Core workflows

- [ ] Inventory registration/restock/move/status works.
- [ ] Duplicate null/blank storage position is rejected.
- [ ] Multi-line request create/submit works.
- [ ] Partial request approval and header derivation work.
- [ ] DRAFT/SUBMITTED cancellation works; approved backward cancellation is rejected.
- [ ] Transfer planning and Administrator approval reserve correctly.
- [ ] Pre-dispatch cancellation releases reservation.
- [ ] Dispatch reduces reserved only.
- [ ] Receipt uses explicit destination and adds only received delta.
- [ ] Temporary whole-line return restores source/decrements destination.
- [ ] Over-return and wrong destination are rejected without partial change.
- [ ] Administrator disposal works; over-disposal is rejected.
- [ ] Dashboard/view totals reconcile with direct SQL.
- [ ] CSV downloads correct filtered rows and neutralizes formula-like text.

## G. Integration evidence and release gate

- [ ] Workbench SELECT confirms a change made through the Next.js frontend.
- [ ] All required genuine screenshots captured.
- [ ] No secret appears in screenshot, log, archive or Git history.
- [ ] `FINAL_AUDIT_REPORT.md` updated with local results.
- [ ] Release archive checksum verified after any local correction.
- [ ] v2 archive is extracted to a fresh folder and the complete acceptance is run from that extraction.
- [ ] Earlier professional archive is kept/archived until v2 is accepted; pre-modernization backup remains protected.

## Acceptance record

| Field | Local result |
|---|---|
| Date/operator | PENDING |
| MySQL server version | PENDING |
| Python version | PENDING |
| Node/npm versions | PENDING |
| Full pytest result | PENDING |
| Frontend type/lint/test/build | PENDING |
| Workbench errors/resolutions | PENDING |
| Browser/API proof operation/query | PENDING |
| Screenshot folder/reference | PENDING |
| Acceptance decision | PENDING — do not mark FINAL RELEASE yet |
