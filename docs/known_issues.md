# SEMS Known Issues and Deliberate Limitations

This register separates **open verification/bugs** from **accepted design limitations**. A frozen limitation is not permission to redesign the 13-relation schema.

## Open bugs / verification blockers

| ID | Status | Impact | Required handling |
|---|---|---|---|
| KI-001 | OPEN — fresh environment verification | MySQL was historically user-verified, but no configured server/safe `_test` URL exists here for a post-modernization full run | Run `.\scripts\final_acceptance.ps1`, record exact current counts/errors and Workbench proof |
| KI-002 | CLOSED — source regression | Dependencies were installed; 131 server-independent Python/API cases, 17 API cases, TypeScript, lint, 10 Vitest tests and production build now pass | Retain current evidence in `VALIDATION_REPORT.md` |
| KI-003 | OPEN — evidence | Genuine post-enhancement Workbench/browser/acceptance screenshots do not exist | Capture SS-01–SS-30 only after real local execution |
| KI-004 | OPEN — human UI acceptance | Source/build checks cannot prove rendered visual quality, responsive behavior or all four role journeys; this sandbox has no browser executable | Complete `VISUAL_QA_REPORT.md` and section E of `LOCAL_ACCEPTANCE_CHECKLIST.md` one controlled role/workflow at a time |
| KI-005 | OPEN — PowerShell host verification | PowerShell is unavailable here, so the orchestrator was statically inspected and its subordinate commands run directly | Execute the exact Windows command and preserve its sanitized log |
| KI-006 | OPEN — development-tool maintenance | ESLint 10.9 currently fails inside the React plugin bundled by `eslint-config-next` 16.3.2; compatible dev-only ESLint 9.39.5 is pinned and lint passes | Re-test ESLint 10 after the Next.js/plugin stack declares compatibility; do not force-upgrade by bypassing lint; see KI-007 for the fresh audit gate |
| KI-007 | OPEN — fresh dependency audit | The sandbox blocks npm registry/audit requests, so no new vulnerability result is claimed for v2 | Run the mandatory npm critical-vulnerability audit inside `.\scripts\final_acceptance.ps1`; any critical finding blocks acceptance |

No unresolved source-level CRITICAL/MAJOR defect is knowingly deferred. Any local MySQL error becomes a new bug entry; do not convert it silently into a design limitation.

## Accepted design limitations

| ID | Limitation | Why acceptable for Baseline v1.0 / required handling |
|---|---|---|
| DL-001 | TRANSFER_ITEM has no destination-inventory FK | Frozen relation retains original/source inventory. Require explicit validated destination at receipt/return and disclose that exact destination lineage is not retained |
| DL-002 | Authentication hashes are external to USER | USER has no password field. Protected bcrypt map by exact email supports a secure academic demo without schema expansion |
| DL-003 | LAB has no activation/status field | Do not expose lab activate/deactivate. USER account status supplies operational access control |
| DL-004 | Temporary return has no returned-quantity attribute | Return complete received temporary lines; PARTIALLY_RETURNED means some lines remain |
| DL-005 | No PARTIALLY_RECEIVED transfer state | Store cumulative line quantities; header stays DISPATCHED until all sent quantities are received |
| DL-006 | Nullable storage coordinates weaken SQL UNIQUE semantics | Service normalizes blanks/NULL/case and checks logical duplicates; DB definition remains frozen |
| DL-007 | INVENTORY repeats lab ownership implied by STORAGE_LOCATION | Frozen ER relationship/query convenience; two triggers and service checks prevent disagreement; normalization proof discloses the controlled exception |
| DL-008 | Disposal valuation uses current INVENTORY.unit_cost | DISPOSAL_RECORD has no historical cost snapshot. Do not present disposed value as immutable historical accounting |
| DL-009 | Seeded users contain no password hashes | Generate local hashes with `generate_demo_hash.py`; never commit demo passwords/hashes intended to remain private |
| DL-010 | CSV is mandatory; printable PDF is not | CSV satisfies frozen reporting evidence. PDF can be a later enhancement without blocking MVP |
| DL-011 | Reset script is deliberately destructive after an exact guard | Back up data, use one intended Workbench session and target only `sems_db` |
| DL-012 | API sessions are process-local | Appropriate for one-machine academic use; restarting Uvicorn signs users out. Distributed/session-persistence infrastructure is future operational scope |
| DL-013 | Streamlit remains duplicated presentation code during acceptance | Intentional rollback protection. Do not retire it until modern UI parity/local acceptance and explicit user approval |
| DL-014 | API health exposes safe local database identity/version information | Useful for academic setup and demonstration; it returns no credentials or connection URL and is intended for local deployment |

## Explicitly out of MVP (not bugs)

Procurement/vendors/purchase orders, maintenance or predictive maintenance, serialized-asset tracking, QR/barcode infrastructure, AI/compatibility recommendations, IoT monitoring, audit-log tables, notifications, remote deployment and public URLs are future scope. Their absence keeps the project academically strong, implementable and faithful to the Source-of-Truth.

## Reporting a new implementation issue

Record:

1. exact script/page/service and smallest reproducible action;
2. MySQL and Python versions;
3. role and laboratory context;
4. complete error text with secrets removed;
5. whether any transaction rows changed;
6. relevant before/after SELECT evidence;
7. classification: bug, environment blocker or frozen limitation.

Update PROJECT_STATE, CHANGELOG, VALIDATION_REPORT and this register before any semantic/schema correction.
