# SEMS Error and Recovery Scenarios

The canonical browser interface displays sanitized API/domain messages. Diagnostic classes and stack traces remain in the Python log; credentials, hashes and full private URLs never belong in frontend errors or screenshots.

| Scenario | Preventive/detection control | Expected safe behavior | Evidence |
|---|---|---|---|
| MySQL server stopped | Connection timeout, pre-ping, healthcheck | Login/active session stops with a concise database-unavailable message; no offline substitute | `preflight_check.py`, healthcheck test |
| FastAPI stopped or wrong public API address | Fetch boundary and health indicator | Frontend shows retryable service-unavailable state; no write is assumed | API client + manual acceptance |
| Opaque session expires/API restarts | Bounded process-local session store | Protected API returns 401 and no data; user signs in again | API session tests |
| Browser payload is malformed | Pydantic input contract plus domain validation | HTTP 422 with safe field/domain guidance; no transaction commits | API contract tests |
| Wrong credentials | Configuration/healthcheck; password never logged | Connection rejected; message exposes exception class only | preflight and `test_healthcheck` |
| Missing/placeholder configuration | Startup connection-issue list | All missing/invalid fields reported without their values | settings tests |
| FK parent removed concurrently | FK RESTRICT/CASCADE and transaction | Statement fails; transaction rolls back; user receives safe operation failure | constraint demo/integration tests |
| Stock becomes insufficient after screen load | Inventory row locked and rechecked | Entire approval/disposal/return fails; no earlier line commits | rules + local concurrency test |
| Two operators allocate same stock | Stable `FOR UPDATE` lock order | First committed transaction wins; second rechecks current free stock and fails/retries | repository/service audit |
| Unauthorized direct service call | Service role/lab checks before mutation | AuthorizationError; no session/stock write starts | service security tests |
| USER role/lab/status changes mid-session | Database actor revalidation | Session is denied and user must sign in again | service security tests |
| Wrong destination lab/component | Explicit destination lookup and locked validation | Receipt/return transaction rolls back | transfer service/manual acceptance |
| Duplicate destination created concurrently | UNIQUE position plus IntegrityError conversion | Whole receipt rolls back with refresh/retry message | receipt contract/local concurrency test |
| Failure after first of multiple stock updates | One `session_scope()` transaction | Context manager rolls back all flushed changes | `test_transactions`; local MySQL workflow test |
| Partial receipt repeats same total | Cumulative bounds and positive delta requirement | No duplicate stock increment; zero-delta confirmation rejected | transfer service/manual acceptance |
| Over-receipt/over-return/over-disposal | CHECKs and locked service quantity rules | Operation rejected before commit | rules and MySQL constraints |
| Duplicate NULL/blank storage coordinate | Blank→NULL normalization and case-insensitive lookup | Logical duplicate rejected despite MySQL NULL UNIQUE semantics | master-data tests |
| CSV formula-like text | Export-cell neutralization | Spreadsheet receives leading apostrophe; numeric negative values remain numeric | analytics tests |

## Transaction troubleshooting rule

After any failed workflow, refresh the page/query before retrying. Do not manually “repair” only one table. Record the actor, target IDs, exact safe error, MySQL/Python versions and whether any rows changed. If reconciliation is uncertain, stop and inspect all involved rows in Workbench before continuing.

## What SEMS deliberately does not do

It does not switch to SQLite/mock data when MySQL is unavailable, auto-reset the database, retry stock mutations blindly, expose SQL tracebacks to users or write credentials to logs.
