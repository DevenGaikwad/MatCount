# Faculty progress review — 11 October 2026

## Evidence inspected

The supplied RC2 archive SHA256 is `8b69a4d00741e7c4d1d93abaa00a9a272a91a0ce66e475f1d33755c90d9ac134`, matching its companion/publication record. All 269 tracked source files match baseline main commit `1326c5aab5343394173cdb764e71de475f51093b`; SOURCE_COMMIT.txt is distribution metadata. The published RC2 tag/archive is preserved.

The 62 clean laptop images cover all SETUP-01–08 and SS-01–52 numbers, with SS-09A/B and SS-25B variants. SS-11 shows all listed acceptance gates PASS, SETUP-07 listeners on 8000/3000, SETUP-08 healthy sems_db/MySQL 8.4.11, and SS-37/46 the partial faculty review and MySQL persistence of request 6. Earlier failed troubleshooting output is not treated as the final result. Values are dated snapshots.

Documentation Parts 1–3 contain genuine command-line implementation captures. Their earlier future-tense evidence/acceptance paragraphs are historical; the new review supplies the current status. The private installed-folder archive did not arrive, so all private laptop files cannot be compared byte-for-byte. No passwords, backups or local environments are published.

## Minimal verified corrections

| File | Defect and correction |
|---|---|
| sql/01_schema.sql | Reproduced MySQL 3823 when CHECK-associated transfer columns used CASCADE actions; removed explicit actions from source/destination/receiver FKs, retaining the FKs and checks with default restriction. |
| tests/integration/test_mysql_constraints.py | CHECK failure is a driver OperationalError/DBAPIError, not consistently IntegrityError; assert exact 3819 and intended constraint name. |
| frontend/package-lock.json | source-map-js 1.2.1 affected by GHSA-68fv-2mgg-jv7q; pin transitive patched 1.2.2 with registry integrity. |
| frontend/features/reports/reports-view.tsx | Numeric field inference could sum IDs; choose a named quantity measure and label the returned-scoped-row boundary. |

The audit gate was not disabled or widened. No migration, reseeding, credential change or live stock rewrite accompanies these source corrections.

## Actual isolated verification

Linux review container, Python 3.12.14, Node 24.19.0/npm 11.9.0, official MySQL 8.4.11; disposable `sems_documentation_test` separate from the user's Windows data:

- Corrected full schema/index/view/routine/trigger/seed build succeeded; original fresh-build CHECK/FK failure reproduced separately.
- SQL contract PASS: 13 relations, 7 views and academic scripts.
- Full pytest: 151 passed, one Starlette/httpx deprecation warning.
- Frontend: typecheck, lint, runtime/lint tooling compatibility and production build PASS; 10 Vitest cases PASS.
- npm audit gate PASS: zero runtime findings; exactly the existing development-only `braces` chain (five packages), no additional finding accepted.
- Optional expansion: 12 catalogue and 24 inventory inserts; rerun adds zero; every original row in all 13 relations unchanged; integrity checks zero; base/view totals agree.
- Temporary normalization reconstruction: 39/39 inventory and 3/3 transfer rows, zero mismatches; no persistent schema migration.

The Windows screenshot acceptance and the independent Linux source review are separate observations. Historical release CI excluded live MySQL integration. Current local tests are not a claim of final institutional acceptance or a general security certification.

## Short live sequence

1. Existing installation: start MySQL, FastAPI on 127.0.0.1:8000 and frontend on 127.0.0.1:3000. Check `/api/health`.
2. Workbench: show server/database identity, 13 base tables, inventory keys and reporting objects.
3. Administrator: show dashboard, catalogue and inventory; explain free versus reserved.
4. Faculty VLSI: show request 6 partial result and retrieve its line quantities independently in SQL.
5. Assistant and Student: show permitted scopes and financial minimization.
6. Show a received transfer, disposal, normalization exceptions and genuine final acceptance.

Configured demo identities are admin@sems.local, faculty.vlsi@sems.local, assistant.vlsi@sems.local and student.vlsi@sems.local. Use privately saved passwords. Do not substitute an Embedded faculty account or remove the .local suffix.

Workbench SQL goes into a query editor tab, not the gray Action Output panel. Execute one selected block; inspect its Result Grid. Workbench is independent of the application and may close after any open transaction is deliberately resolved. PowerShell starts the servers; `mysql.exe` is an equally valid SQL client.

If the browser is unavailable, show genuine dated evidence and read-only schema/JOIN/view/routine queries while explicitly explaining the current startup limitation. Do not reset the database to recover a demonstration.

## Remaining actions

Restart/oral rehearsal, the applicable faculty batch, guide review, unsigned certificate and an authentic plagiarism report remain student/institutional actions. Optional live expansion must proceed precheck → fresh matched-version backup → catalogue screenshot approval → inventory screenshot approval → read-only verification. No proposed live insert was executed by this review.

## Primary technical sources

- [MySQL CHECK constraint restrictions](https://dev.mysql.com/doc/refman/8.4/en/create-table-check-constraints.html)
- [MySQL locking reads](https://dev.mysql.com/doc/refman/8.4/en/innodb-locking-reads.html)
- [source-map-js advisory and patched version](https://github.com/advisories/GHSA-68fv-2mgg-jv7q)
