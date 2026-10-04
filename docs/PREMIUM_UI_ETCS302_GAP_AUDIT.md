# SEMS Premium UI + ETCS302 Advanced DBMS Gap Audit

**Audit date:** 2026-08-24  
**Starting release:** `SEMS_Final_Professional_Release.zip`  
**Starting release SHA-256:** `ff57d20daf33dad64b2b151c61535f77eb93f700e8cfbd051890af02075e1d00`  
**Protected production boundary:** exactly 13 base relations and seven reporting views  
**Purpose:** pre-change evidence for the authorized v2 academic and visual enhancement pass

## A. Current frontend visual-quality assessment

The Next.js interface is already coherent, responsive and materially stronger than the preserved Streamlit fallback. It has a split login, authenticated shell, role-aware navigation, reusable cards/tables/dialogs, status badges, workflow timeline, loading/error/empty states and responsive breakpoints. It is a strong professional first pass, but not yet a fully evidenced premium release: table controls are limited, visual tokens are partly ad hoc, several feature files are densely formatted, module-level search/filtering is inconsistent, dialogs use a custom focus implementation, and no post-v2 multi-viewport visual evidence exists.

## B. Current design system

`frontend/app/globals.css` defines DESPU-inspired orange, amber, maroon, warm-white, charcoal, semantic colours, two shadow levels, cards, buttons, inputs, tables, dialogs, charts, timelines and responsive rules. Gaps: tokens do not yet cover a complete spacing/radius/type/motion system; hard-coded colours remain; dark/navy hierarchy and subdued institutional surfaces need refinement; skeletons, table density and accessible reduced-motion treatment need strengthening.

## C. Current component libraries

The browser dependencies are intentionally minimal: Next.js, React and React DOM. Tailwind CSS is a development/build dependency. UI primitives, icons, tables, dialogs and charts are project-owned. There is no shadcn/ui, Radix UI, React Aria, TanStack Table, Lucide, React Hook Form, Zod or animation library. Any addition must solve a demonstrated accessibility or UX problem; no library migration is justified merely by popularity.

## D. Current role model

The frozen `USER.role` domain is `STUDENT`, `FACULTY`, `LAB_ASSISTANT`, `ADMINISTRATOR`. Navigation hiding is supplemented by service-level role, laboratory and actor revalidation. Students create/read their own requests; Faculty reviews requests and monitors transfers; Lab Assistants manage own-lab storage/inventory and transfer operations; Administrators manage global masters, approvals, disposal and global reporting. This is a genuine multi-user model and does not need another relation.

## E. Current price/financial-field authorization

**Critical gap.** `v_inventory_detail` and `v_component_stock_summary` contain `unit_cost`, `available_value` and `inventory_value`; dashboard KPI and stock-by-lab queries contain valuation; student report permissions currently include both financial-bearing views; and `/inventory` returns the full inventory view. React shows fixed cost/value columns. Therefore a Student can receive financial values from the API even if a future CSS-only hide were added. Faculty visibility is also not governed by an explicit policy. Resolution: Admin has global financial visibility; Lab Assistant has own-lab operational cost visibility; Faculty and Student receive no cost/valuation fields. Redaction must occur in the service/API response before serialization and CSV generation, with automated negative tests.

## F. Current 13-relation schema confirmation

Static contract validation confirms these exact production relations: `LAB`, `LAB_CONTACT`, `USER`, `USER_PHONE`, `COMPONENT_CATEGORY`, `COMPONENT`, `STORAGE_LOCATION`, `INVENTORY`, `COMPONENT_REQUEST`, `REQUEST_ITEM`, `TRANSFER`, `TRANSFER_ITEM`, `DISPOSAL_RECORD`. No v2 production-table change is required or authorized.

## G–K. Current theory-unit coverage

| Unit | Current coverage | Gap status |
|---|---|---|
| I — DBMS and architecture | Layered architecture, ER-to-relational mapping, schema dictionary, relationships/cardinalities, relational-model rationale | Historical model comparison, three-schema architecture, abstraction/data independence and DBMS component explanation need a unified academic report |
| II — Relational model/design | PK/FK/UNIQUE/CHECK domains, joins/views, normalization proof, associative and multivalued relations | Relation/tuple/domain vocabulary, relational-algebra mapping, complete FD/candidate-key matrix, MVD explanation and defensible relation-by-relation normal-form evidence need expansion |
| III — SQL/stored programming | DDL/DML, joins/aggregates, seven views, indexes, one procedure, one function, two triggers, rollback and EXPLAIN demos | Advanced selects, correlated queries, set operations, CTE/window function, OUT/conditional routine, cursor, DCL and vendor-specific sequence/synonym/assertion treatment are missing |
| IV — Transactions | Python transaction boundaries, row locking, stable lock order, rollback demo and recovery scenarios | SAVEPOINT, two-session locking/concurrency, safe deadlock education, schedules/serializability/isolation/recovery evidence need dedicated scripts and documentation |
| V — NoSQL | No production NoSQL dependency, which is architecturally correct | Optional isolated MongoDB CRUD sample, CAP and relational-vs-NoSQL explanation are absent |

## L–U. Current laboratory-assignment coverage

| Assignment | Current evidence | Gap status |
|---|---|---|
| 1 — ER/EER | Actual entities, attributes, keys, cardinalities, mapping and normalization documents | Consolidate multivalued attributes/participation and diagram evidence references |
| 2 — DDL | Complete 13-table DDL, constraints, AUTO_INCREMENT and indexes | Add safe ALTER/DROP test-schema examples plus MySQL sequence/synonym explanation |
| 3 — DML | Seed INSERTs and application INSERT/UPDATE/DELETE/SELECT | Add one faculty-friendly script covering equality, range, LIKE, ORDER BY and LIMIT |
| 4 — Advanced SQL | Production views and aggregates | Add explicit COUNT/SUM/AVG/MIN/MAX, GROUP BY/HAVING and LEFT/RIGHT JOIN demonstrations without double counting |
| 5 — Views | Seven correctly grained production views | Improve view abstraction/security demonstration; no extra view is justified |
| 6 — Nested queries | Scalar KPI subqueries | Add non-correlated, correlated, IN, EXISTS, NOT EXISTS and aggregate subqueries |
| 7 — Procedures/functions | One IN-parameter procedure and one deterministic function | Add legitimate OUT/multi-parameter/conditional reporting procedure; preserve transaction logic in services |
| 8 — Triggers | Two production validation triggers | Add isolated audit and synchronization examples in academic demo schema only |
| 9 — Cursor | None | Add an isolated MySQL cursor procedure and set-based comparison |
| 10 — Mini Project | Full frontend, MySQL schema, workflows, views, indexes, routine/function/triggers and documentation | Strengthen academic traceability, RBAC proof, screenshots and fresh acceptance evidence |

## V. Missing syllabus concepts

Relational-algebra examples; explicit MVD discussion; set operations; advanced nested/correlated queries; CTE/window reporting; OUT/conditional routine; cursor lifecycle; DCL roles/GRANT/REVOKE/SHOW GRANTS; SAVEPOINT; two-session row-lock demonstration; deadlock education; recovery/checkpoint theory; isolated trigger-audit example; MySQL vendor differences for assertions/sequences/synonyms; optional MongoDB CRUD/CAP comparison; formal ETCS302 traceability matrix; query-optimization report; comprehensive academic coverage report; expanded viva material.

## W. Concepts inappropriate to force into production

Historical hierarchical/network/object-oriented models, audit table, MongoDB, destructive deadlock experiments, synthetic production relations, artificial self-joins, unsupported sequence/synonym/assertion syntax and redundant views do not belong in `sems_db`. They will be documented or isolated under `academic_demo/`.

## X. MySQL-specific incompatibilities

MySQL 8.4 does not provide SQL-standard `CREATE ASSERTION`, standalone SQL-standard `CREATE SEQUENCE`, or `CREATE SYNONYM`. SEMS will use CHECK/FK/UNIQUE/triggers/services for assertion-like rules, `AUTO_INCREMENT` for identity generation, and views only as a documented name/abstraction analogue—not as a falsely claimed synonym feature.

## Y. Proposed premium UI refinements

Complete design tokens; improved typography and spacing; clearer role/lab context; consistent page/tool bars; stronger tables with density and column controls where useful; server-backed role-sensitive columns; better dashboard attention hierarchy; request/transfer detail composition; report filtering/summary polish; form guidance; reduced-motion support; stronger skeletons; mobile table treatment; consistent financial badges; and route-by-route visual QA.

## Z. Proposed advanced DBMS additions

Separate faculty-safe scripts for relational algebra, advanced selects, joins/aggregates, nested queries, views/indexes/EXPLAIN, routines, cursor, trigger audit, transactions/SAVEPOINT, concurrency, deadlock and DCL. Add isolated NoSQL examples, full FD/normalization evidence, optimization evidence and syllabus mapping. Production schema/view counts remain unchanged.

## AA. Existing files to modify

`services/rbac.py`, `services/analytics_service.py`, relevant API routes/serializers, report repository queries where projection improves security, frontend permissions/types/components/features/CSS, frontend tests/package metadata if justified, SQL routine/support files only where non-breaking, validation scripts, `final_acceptance.ps1`, README, architecture, Workbench/faculty/viva/test/setup/user/release documentation, changelog and manifests.

## AB. Files/directories to add

`academic_demo/` with SQL and NoSQL subdirectories; `docs/ETCS302_SYLLABUS_TRACEABILITY_MATRIX.md`; `docs/DBMS_ACADEMIC_COVERAGE_REPORT.md`; `docs/QUERY_OPTIMIZATION_REPORT.md`; expanded normalization/FD report; formal RBAC matrix; v2 professionalization report; focused API/service/frontend security tests.

## AC. Regression risks

Accidental schema/view-count change; redaction breaking staff forms; frontend assuming absent columns; lab-scope widening; report CSV leakage; duplicate SQL logic; demo scripts touching production; unsafe test target; MySQL syntax drift; dependency incompatibility; acceptance script becoming destructive; and claiming visual/MySQL validation that was not run.

## AD. Test strategy

Add service and API tests proving Student/Faculty financial fields are absent, Student report scope is own/lab-limited, exports exclude sensitive fields, unauthorized mutations fail, stale actors fail, injection-like input remains bound/validated and 13/7 contracts remain exact. Run fresh Python, API, frontend, TypeScript, ESLint, build, audit and secret scans. Run integration only against `sems_test`; fresh Windows/MySQL and visual acceptance remain explicit local gates.

## AE. Release/versioning strategy

Preserve the starting archive and historical pre-modernization rollback. Build a new `SEMS_Final_Academic_Professional_Release_v2.zip` plus SHA-256 only after fresh server-independent validation. Do not overwrite the prior professional archive or call v2 the final academic release before local acceptance.

## AF. Local cleanup/handoff strategy

KEEP the pre-modernization backup, faculty sources and new v2 artifacts. ARCHIVE the unaccepted v1 professional release until v2 passes. Mark duplicate v1 extractions/caches/download copies SAFE TO DELETE only after SHA verification, clean extraction, configuration migration, one-command acceptance, MySQL integration, role tests, visual acceptance and Workbench evidence. Never delete `sems_db`, faculty material or the only real local `.env`.

## Audit decision

No protected production-schema change is necessary. Proceed in the authorized order: backend financial/RBAC enforcement; isolated ETCS302 demonstrations; premium UI refinement; regression tests; documentation; acceptance automation; versioned packaging.
