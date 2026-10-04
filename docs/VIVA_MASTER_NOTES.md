# SEMS Viva Master Notes

## Project and design

**1. What problem does SEMS solve?**  
Disconnected lab registers cannot reliably answer what component exists, where it is, what is free/reserved, who requested it, whether it moved, returned or was disposed. SEMS centralizes those related facts and controls their lifecycle.

**2. Why is SEMS not just inventory management?**  
The core includes normalized contacts/phones, multi-line requests, faculty quantity review, request-linked inter-lab transfer, reservation/dispatch/receipt/return, Administrator disposal, RBAC, views and analytics.

**3. Why use a DBMS instead of Excel?**  
MySQL enforces keys, FKs, domains, constraints and concurrent atomic transactions. Excel may display rows but cannot reliably enforce multi-user referential integrity and row-locked stock transitions.

**4. What is the full-project database?**  
`sems_db` with 13 base relations. `smart_electronics_lab_ddl` is only the smaller Assignment 2/3 coursework subset and must not be confused with the mini-project.

**5. ER versus EER?**  
ER models entities, attributes and relationships. EER extends that conceptual language with richer role/participation and specialization concepts. SEMS mainly needs role-labelled relationships and associative/multivalued mappings; it does not invent unnecessary specialization tables.

**6. What is an entity and a relationship?**  
An entity is a distinguishable object/fact type such as COMPONENT or LAB. A relationship connects types, such as LAB maintains INVENTORY or TRANSFER contains TRANSFER_ITEM.

**7. What are cardinality and participation?**  
Cardinality gives maximum multiplicity, such as one request to many request items. Participation gives minimum multiplicity: a DRAFT request may temporarily have zero lines, but submission enforces at least one; every request item must belong to exactly one request.

## Keys and mapping

**8. Primary key, foreign key and candidate key?**  
A PK is the chosen unique row identifier. An FK references a candidate/primary key in another relation. A candidate key is any minimal unique identifier, such as USER.email; the surrogate user_id is the selected PK.

**9. Why composite PKs for LAB_CONTACT and USER_PHONE?**  
The owner/value pair naturally identifies a multivalued fact. It prevents repeating phone columns and duplicate values for the same owner.

**10. Why is REQUEST_ITEM associative?**  
Requests and components are conceptually M:N. Quantity requested/approved, state and remarks describe that association, so they belong in REQUEST_ITEM.

**11. Why is TRANSFER_ITEM associative?**  
A transfer can allocate several source inventory rows and an inventory row can participate in many transfers over time. Sent/received quantities, due/return dates and conditions belong to the allocation.

**12. Why is USER quoted?**  
`USER`/`user` is a MySQL reserved word/contextual identifier. DDL/raw SQL uses backticks and SQLAlchemy uses a forced quoted table name.

## Normalization

**13. Explain 1NF, 2NF and 3NF in SEMS.**  
1NF: scalar columns and repeating contacts/items become rows. 2NF: no non-key fact depends on part of a composite key. 3NF: descriptive facts remain in their master table rather than depending transitively on a transaction key.

**14. Is every relation BCNF?**  
No blanket claim. Most have BCNF intent under declared keys. INVENTORY carries a frozen controlled redundancy because storage_location_id semantically determines lab_id; triggers/services keep them equal. Nullable location coordinates also qualify the natural-key claim. This is explicitly documented.

**15. Does INVENTORY.lab_id violate normalization?**  
Under the semantic FD from location to lab, it is a controlled 3NF/BCNF exception. It is retained by the frozen ER mapping for direct lab ownership/querying and protected against disagreement. The correct answer is disclosure, not pretending the FD does not exist.

**16. What anomalies are reduced?**  
Component/category/lab descriptions update once; contacts and items can be inserted without changing columns; headers are not repeated per line; FKs prevent orphans; disposal remains event history.

## Constraints and SQL

**17. Why AUTO_INCREMENT surrogate IDs?**  
They provide stable compact references independent of editable names. Natural candidate keys remain UNIQUE where appropriate.

**18. Why both service validation and database CHECK/FK rules?**  
Services give contextual, user-friendly workflow messages. Database constraints remain the final integrity boundary for any client, including Workbench.

**19. What is the nullable UNIQUE issue?**  
MySQL UNIQUE permits multiple rows where key components are NULL. The storage service converts blanks to NULL and compares `COALESCE/lower` values before insert/update; concurrent conflicts still roll back.

**20. What are indexes?**  
Indexes are access structures used by the optimizer. SEMS adds query-justified status/date/lab/component indexes and avoids claiming fabricated speedups. PK/UNIQUE/FK indexes are not blindly duplicated.

**21. What does EXPLAIN show?**  
The estimated execution plan: access type, possible/chosen key, join references and estimated rows. It is not a timing benchmark.

**22. Why views?**  
Views centralize reusable joins/aggregations and publish an explicit row grain. Seven views cover inventory, stock summary, low stock, request progress, transfer detail, overdue returns and disposal.

**23. Procedure versus function?**  
The function returns a scalar available value and is callable in expressions. The procedure returns a component-availability result set and is invoked with CALL.

**24. Why only two triggers?**  
They enforce a narrow cross-table invariant: inventory lab equals storage-location lab. Workflow transitions stay in Python services to avoid duplicated, divergent logic.

## Transactions and stock

**25. Explain ACID in SEMS.**  
Atomicity: all workflow rows commit or roll back. Consistency: constraints/invariants hold. Isolation: locks prevent competing stock changes from using stale values. Durability: committed InnoDB changes persist.

**26. What is rollback?**  
It discards all changes in an uncommitted transaction. `session_scope()` rolls back on exceptions; `demo/02` visibly restores a value.

**27. Why `SELECT ... FOR UPDATE`?**  
It locks selected mutable rows until commit/rollback, so availability is rechecked against the serialized current value before a stock change.

**28. Why stable lock order?**  
Every multi-row workflow locks sorted inventory IDs. Competing transactions request rows in the same order, reducing deadlock probability.

**29. Define available and reserved.**  
Available is physical stock free for allocation. Reserved is approved stock awaiting dispatch. Both are nonnegative.

**30. Why does dispatch not subtract available?**  
Approval already applied `available -= Q; reserved += Q`. Dispatch applies only `reserved -= Q`. Subtracting available again would double-count the same movement.

**31. How does cancellation work?**  
Before dispatch, an approved transfer releases `available += Q; reserved -= Q`. Cancellation after dispatch is rejected.

**32. How are multi-line failures handled?**  
The header, lines and all stock rows share one transaction. A later-line error raises before commit, so earlier flushed updates roll back.

## Workflows and limitations

**33. How is partial request approval represented?**  
Each line stores requested and approved quantities. Zero means rejected, a smaller positive amount is PARTIALLY_APPROVED, and equality is APPROVED. Header state is derived from all lines.

**34. Who approves what?**  
Faculty/Administrator reviews request quantities for the requesting lab. Transfer approval/reservation is Administrator-only under the latest frozen decision. Lab Assistant/Administrator performs operational dispatch/receipt/return.

**35. Why can approval not be revised after allocation?**  
Transfers may already rely on that approved ceiling. Changing it would make allocated quantities inconsistent; service freezes review once allocation begins.

**36. How does partial receipt work without PARTIALLY_RECEIVED?**  
Each line stores a cumulative received quantity bounded by sent quantity. The header remains DISPATCHED while any line is incomplete and becomes RECEIVED only when all totals equal sent quantities.

**37. Where is destination inventory stored?**  
It is not stored on TRANSFER_ITEM. The operator explicitly selects/creates and validates it at receipt/return. Exact post-receipt destination lineage is a disclosed frozen-schema limitation.

**38. Why whole-line temporary return?**  
The schema has return date/condition but no returned-quantity column. A completed received line is returned as a whole; PARTIALLY_RETURNED means some temporary lines remain.

**39. Condition on issue versus return?**  
Issue condition is written at dispatch. Return condition is written only when a temporary item actually returns. There is no persistent receipt-condition field.

**40. How is disposal safe?**  
Administrator role is revalidated, inventory is locked, quantity must be positive and no greater than free stock, and the history insert plus decrement commit atomically.

## Application and security

**41. Why use React/Next.js instead of keeping Streamlit as the final UI?**  
Streamlit proved the workflow quickly and remains a fallback, but its rerun/widget/DOM model constrained a persistent institutional shell, complex modal workflows, responsive tables and fine interaction control. Next.js/React supplies a maintainable component model and production build while leaving database/business logic in Python.

**42. Why TypeScript and Tailwind?**  
TypeScript catches client/API contract mistakes before runtime. Tailwind utilities plus a small project design system produce consistent spacing, responsive behavior and states without moving semantics into styling. Neither affects the database.

**43. Why is there a FastAPI layer?**  
A browser cannot safely call Python functions or MySQL directly. FastAPI is a thin typed transport boundary: it authenticates an opaque session, validates payload shape, calls an existing service and serializes a safe response. Routes do not own business rules or repositories.

**44. Why must Node not connect to MySQL?**  
Direct browser/Node DB access would expose credentials, duplicate authorization and bypass Python transactions. Keeping one path—frontend → API → services → repositories—preserves the validated source of truth and is easier to test and explain.

**45. Why SQLAlchemy and PyMySQL?**  
SQLAlchemy provides mappings, parameterized queries and session/transaction management. PyMySQL is the MySQL DBAPI driver used by the SQLAlchemy URL.

**46. Repository versus service versus API route?**  
Repositories persist/query. Services decide authorization, validation, state changes, locks and transaction consistency. API routes transport validated data; frontend components only collect/display.

**47. What is RBAC and why is UI hiding insufficient?**  
RBAC restricts actions by role and lab scope. A hidden button can be bypassed; therefore service methods independently reject unauthorized calls and revalidate the database user.

**48. Why are password hashes outside USER, and what reaches the browser?**  
The frozen USER relation has no password attribute. Protected local bcrypt mappings authenticate an email, then USER supplies authoritative role/lab/status. No plaintext or hash is committed.

The browser receives only an opaque expiring token and public API address. Database credentials and hashes remain in the Python process. Process-local sessions are intentionally suitable for the single-machine academic target; a restart requires login again.

**49. How is CSV injection handled?**  
Formula-like text beginning with `=`, `+`, `-` or `@` after whitespace receives an apostrophe. Numeric negative values remain numeric; internal/secret fields are not exported.

**50. What is Workbench’s role?**  
It is an independent SQL client for build, inspection and faculty proof. It is not MySQL Server; neither Next.js/FastAPI nor Streamlit depends on Workbench being open.

**51. How do tests avoid damaging the demo DB?**  
Integration tests require `SEMS_TEST_DATABASE_URL` and reject targets not ending `_test`. Each test uses a rollback transaction. `sems_db` is never accepted as test proof.

**52. What does the one-command acceptance script prove?**  
It checks structure/runtimes, Python and SQL contracts, live MySQL identity and 13 relations, safe `_test` targeting, full pytest/API tests, frontend type/lint/test/build and secret hygiene. It is read-only toward `sems_db` and returns nonzero on mandatory failure.

**53. What are the main limitations?**  
No persisted destination inventory lineage, external auth hashes, no LAB status, whole-line returns, current-cost disposal valuation, process-local API sessions and pending fresh local MySQL/UI acceptance. These are documented design/environment limits, not hidden bugs.

**54. What remains future scope?**  
Procurement, vendors, maintenance, serialized assets, QR/barcode infrastructure, AI recommendations, IoT, notifications, audit-log tables, deployment and predictive features. None is in MVP.

## ETCS302 advanced viva

**55. Functional dependency versus multivalued dependency?**  
`email → user_id, lab_id, full_name, role, status` is a functional dependency: one email determines one user row. Conceptually `lab_id ↠ contact_number` is multivalued because a lab has an independent set of contacts. LAB_CONTACT decomposes that set into atomic rows.

**56. Why do you not simply claim every table is BCNF?**  
A correct proof must include semantic dependencies, not only declared keys. STORAGE_LOCATION determines its LAB, so INVENTORY’s repeated lab ownership is a frozen, integrity-protected exception. Declaring universal BCNF would be academically weaker than disclosing it.

**57. What is a correlated subquery?**  
It references an outer-row value. The demo finds inventory positions below their own laboratory average by comparing each outer INVENTORY row to an inner average filtered by the same lab_id.

**58. CTE versus derived table versus window function?**  
A derived table is a subquery in FROM; a CTE gives a named query expression; a window function computes across a partition without collapsing detail rows. The stock-rank query uses a CTE then DENSE_RANK within each lab.

**59. Why use a cursor only as academic evidence?**  
The cursor proves DECLARE, OPEN, FETCH, loop, NOT FOUND handler and CLOSE. Production uses the equivalent GROUP BY because set processing is shorter, easier for the optimizer and normally more efficient.

**60. What do the trigger demos prove without changing the production schema?**  
Production triggers validate inventory/location lab equality. An isolated demo schema additionally shows synchronization and audit logging. Its audit table is explicitly not one of the 13 SEMS relations.

**61. What is MySQL’s equivalent to a sequence, assertion and synonym here?**  
AUTO_INCREMENT provides numeric identities. MySQL has no CREATE ASSERTION, so CHECK/FK/UNIQUE/triggers/services enforce rules. It has no CREATE SYNONYM; a view can provide a named query abstraction but is not falsely presented as a full synonym.

**62. Application RBAC versus DCL?**  
DCL controls what a MySQL account can do to database objects using GRANT/REVOKE. Application RBAC controls what a Student, Faculty, Lab Assistant or Administrator can do in SEMS. The frontend never receives a MySQL account/password.

**63. How are Student financial fields protected?**  
The API/service response policy removes cost and valuation keys before serialization and CSV export; the Student availability response uses an allowlist that also omits location and reserved stock. React hiding is only a second usability layer. Automated API/service tests call protected endpoints directly and verify 403 or minimized fields.

**64. What is a savepoint and why is it not used everywhere?**  
A savepoint marks an intermediate point for `ROLLBACK TO SAVEPOINT`. The syllabus demo uses it in a disposable transaction. SEMS stock workflows normally need full atomicity, so partial commit would be the wrong default.

**65. Explain dirty read, non-repeatable read, phantom and lost update.**  
Dirty read sees uncommitted data; non-repeatable read sees a changed committed row; phantom sees new matching rows; lost update overwrites another change. READ COMMITTED prevents dirty reads, while `FOR UPDATE`, guarded arithmetic and full revalidation protect stock transitions.

**66. How does InnoDB recover after a crash?**  
Conceptually, undo information removes incomplete effects and redo reapplies committed effects as required; write-ahead logging and checkpoints bound safe recovery. The project demonstrates rollback rather than destructively crashing a server.

**67. Explain CAP correctly.**  
When a distributed system experiences a network partition, it must trade always-consistent responses against always-available responses for affected operations. CAP is not a rule that a normal single-node database always chooses only two of three properties.

**68. Why is MongoDB optional rather than part of SEMS runtime?**  
A document store could hold flexible catalogue metadata, and the isolated script demonstrates CRUD/projection. The canonical workflows need relational FKs, normalized associations and multi-row transactions, so MySQL remains the source of truth and MongoDB is a syllabus-only extension.
