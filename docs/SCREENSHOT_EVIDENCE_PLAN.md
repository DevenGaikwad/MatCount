# SEMS Screenshot Evidence Plan

Screenshots are captured only from genuine local execution. Use a neutral desktop, crop unrelated personal information, hide connection passwords and preserve enough application/Workbench context to prove the result. Do not fabricate, composite or AI-generate evidence.

| ID | Required screenshot | Exact purpose / visible evidence |
|---|---|---|
| SS-01 | `SELECT VERSION()` | MySQL Server reports 8.4.11 |
| SS-02 | Workbench SCHEMAS panel | `sems_db` selected; not Assignment database |
| SS-03 | Expanded Tables node | All 13 base relations visible in one/two clearly sequential captures |
| SS-04 | INVENTORY or TRANSFER structure | Columns plus PK/FK/index information |
| SS-05 | Seed count/query output | Representative seeded records and coherent quantities |
| SS-06 | Meaningful JOIN | Request → transfer → component/source-stock result |
| SS-07 | Reporting view | Low stock, request progress, transfer detail or overdue return result |
| SS-08 | Constraint demo | EXPECTED failure message and unchanged-row verification; no secret/query ambiguity |
| SS-09 | Transaction demo | Inside value and post-ROLLBACK restored flag |
| SS-10 | EXPLAIN result | Chosen key/access information for one important query |
| SS-11 | Final acceptance terminal | `.\scripts\final_acceptance.ps1`, current test/build totals and `FINAL RESULT: PASS` |
| SS-12 | SEMS professional login | Institutional split login; no password/demo credential/navigation visible |
| SS-13 | Dashboard | Role context, KPIs and one readable chart |
| SS-14 | Inventory | Cross-lab availability and free/reserved columns |
| SS-15 | Request workflow | Multi-line request or partial-approval result |
| SS-16 | Transfer workflow | Approved/reserved, dispatched or receipt destination selection |
| SS-17 | Disposal/report | Authorized disposal history or a report plus CSV control |
| SS-18 | Next.js → Workbench proof | Before/after Workbench query proving the browser/API write persisted in the same `sems_db` |
| SS-19 | Role-aware shell | Sidebar/top bar/user identity for one non-Administrator role with prohibited modules absent |
| SS-20 | Responsive interface | A genuine tablet/mobile or narrow desktop view showing usable navigation/forms |
| SS-21 | Stored procedure | CALL with IN/OUT values and readable result set |
| SS-22 | Stored function | scalar function input/output |
| SS-23 | Trigger | production trigger definition or isolated expected validation/audit result, with schema name visible |
| SS-24 | Cursor | cursor procedure result plus script showing OPEN/FETCH/CLOSE |
| SS-25 | Concurrency | two Workbench tabs showing lock wait/rechecked guarded allocation in demo schema |
| SS-26 | DCL | sanitized SHOW GRANTS result with no password/account secret |
| SS-27 | Student financial restriction | Student inventory/report response with useful availability and no cost/value/coordinates |
| SS-28 | Faculty request review | submitted multi-line request with per-line review controls/status |
| SS-29 | Administrator dashboard | global oversight and valuation visible only to authorized role |
| SS-30 | Premium login | complete 1366×768 page with focus/validation state and no demo password |

## Capture discipline

1. Complete local acceptance first; do not use placeholders as evidence.
2. Use deterministic demo IDs/reasons and record them in the demo notes.
3. Capture the command/query and its output together where possible.
4. Remove/crop `.env`, secrets, connection passwords, browser accounts and unrelated files.
5. Name files `SS-01_mysql_version.png` through `SS-30_premium_login.png`.
6. Do not add screenshots to the release archive until reviewed for secrets and truthfulness.

## Pending status

No Workbench or application evidence screenshot is fabricated. All SS-01–SS-30 items remain **PENDING LOCAL CAPTURE** until the configured Windows/MySQL acceptance is performed.
