# SEMS ETCS302 Academic Coverage Report

**Project:** Centralized Electronic Component and Laboratory Asset Management System / Smart Electronics Management System (SEMS)  
**Canonical DBMS:** MySQL Community Server 8.4.11 LTS  
**Boundary:** 13 production relations and seven production reporting views; syllabus-only destructive examples are isolated in `sems_academic_demo`.

This report answers five questions for each syllabus area: whether it exists, where it exists, why SEMS uses (or does not force) it, how faculty can demonstrate it, and the corresponding viva explanation. “Source complete” does not claim that a fresh local MySQL run has occurred.

## Unit I — Database systems and architecture

| Topic | Implemented? | Where and why | How to demonstrate | Viva explanation |
|---|---|---|---|---|
| DBMS definition, purpose, applications | Documented | `DBMS_ARCHITECTURE_AND_DATA_MODELS.md`; establishes why shared asset facts need a DBMS | compare a manual register with a constrained cross-lab request | DBMS manages durable shared data, queries, integrity, authorization, concurrency and recovery |
| DBMS vs file processing | Documented | same report; avoids duplication, isolated updates and weak concurrency | trace one component across lab, inventory, request and transfer | normalization + keys + transactions solve problems a folder of spreadsheets cannot reliably solve |
| database/three-schema architecture | Implemented | external role pages, conceptual 13-table model, internal InnoDB/index layer | show Student projection, schema, then EXPLAIN | presentation and physical plans change without changing logical meaning |
| abstraction/data independence | Implemented | frontend modernization preserved the schema; indexes remain internal | show architecture and freeze contract | logical and physical data independence are demonstrated by independent layers |
| hierarchical/network/relational/object models | Documented | model comparison report; only relational is production | explain why transfer/request links do not form one tree | relational is selected for declarative joins, integrity and transactions; alternatives are not forced |
| DBMS components | Documented/demonstrated | query processor via EXPLAIN; storage/transaction manager via InnoDB | inspect optimizer plan and transaction demo | processor plans SQL; storage/transaction subsystems manage pages, locks and recovery |
| design process and ER/EER mapping | Implemented | freeze register, ER mapping, cardinality and schema documents | walk LAB → INVENTORY → TRANSFER relationships | requirements become conceptual entities/relationships, then constrained relations |

## Unit II — Relational model and database design

| Topic | Implemented? | Where and why | How to demonstrate | Viva explanation |
|---|---|---|---|---|
| relation/tuple/attribute/domain | Implemented | `sql/01_schema.sql`, `schema_dictionary.md` | DESCRIBE INVENTORY and inspect rows | table, row, column and allowed value set respectively |
| keys/domain/referential constraints | Implemented | PK/FK/UNIQUE/CHECK/ENUM across 13 relations | SHOW CREATE TABLE REQUEST_ITEM/TRANSFER_ITEM | keys identify/link rows; domain and FK rules reject invalid facts |
| selection/projection/rename | Demonstrated | `01_relational_algebra_examples.sql` | execute first three read-only queries | WHERE is selection, selected columns are projection, aliases represent rename |
| union/intersection/difference/product | Demonstrated | MySQL 8.4 UNION/INTERSECT/EXCEPT and bounded CROSS JOIN in same script | execute against seeded transfers/labs/categories | set operators require union-compatible columns; product is bounded because it grows multiplicatively |
| joins | Implemented | views, verification queries and join demo | run complete request→transfer→inventory join | join combines related tuples using FK predicates |
| FD and MVD | Documented/proved | `NORMALIZATION_PROOF.md` | explain USER email key and LAB_CONTACT decomposition | FDs determine single facts; independent phones/contacts create multivalued dependencies |
| 1NF, 2NF, 3NF, BCNF | Documented/proved | per-relation key/dependency catalogue | defend REQUEST_ITEM and disclose INVENTORY exception | no repeating groups/partial/transitive dependencies overall; no false blanket BCNF claim |

## Unit III — SQL and MySQL stored programming

| Topic | Implemented? | Where and why | How to demonstrate | Viva explanation |
|---|---|---|---|---|
| DDL/data types/CREATE | Implemented | `sql/00`–`05`, schema dictionary | build/inspect in script order | DDL defines objects and integrity |
| ALTER/DROP | Demonstrated safely | `00_ddl_vendor_equivalents.sql` only in disposable demo schema | run complete script | production baseline is not altered merely for a teaching checkbox |
| INSERT/UPDATE/DELETE | Implemented + isolated demo | seed/services; temporary table in `02_dml_and_advanced_selects.sql` | run temp-table example, then a safe UI write | DML changes tuples; workflows apply validation and transactions |
| predicates/order/limit/null/distinct | Demonstrated | `02_dml_and_advanced_selects.sql` | run script | predicates restrict rows; ORDER/LIMIT bound results; NULL needs IS NULL semantics |
| joins/aggregates/GROUP BY/HAVING | Implemented | views and `03_joins_aggregates.sql` | run lab/category summaries | GROUP BY defines result grain; HAVING filters groups after aggregation |
| RIGHT JOIN | Demonstrated where meaningful | labs retained even with no inventory in join demo | compare with equivalent LEFT JOIN | RIGHT JOIN is valid but LEFT JOIN is usually clearer |
| self-join | Not implemented | no legitimate parent/adjacency relation; LAB joined twice by source/destination roles is not falsely called self-join | explain the role join | advanced syntax is not forced without a real semantic case |
| scalar/date/string/numeric/CASE/COALESCE | Demonstrated | join/aggregate script and views | inspect stock-health labels and ratios | functions transform values; CASE expresses conditional result; COALESCE handles NULL |
| nested/correlated/EXISTS/NOT EXISTS | Demonstrated | `04_nested_correlated_queries.sql` | run examples | correlated subquery is evaluated with values from its outer row; EXISTS tests existence |
| derived table, CTE, window function | Demonstrated | approval ratio and lab stock rank | show DENSE_RANK partitioned by lab | CTE improves readability; window functions keep row detail while computing within a partition |
| views | Implemented | seven views in `sql/03_views.sql` | SHOW CREATE VIEW and SELECT | view is a reusable virtual relation with a declared grain |
| indexes and optimization | Implemented/demonstrated | `sql/02_indexes.sql`, EXPLAIN script/report | compare prefix vs leading-wildcard plan | index usefulness depends on predicate order/selectivity and cost estimates |
| procedures | Implemented | production `sp_component_availability`; demo IN/OUT routine | CALL routines | procedure can return result sets/output values and may encapsulate reusable DB-side work |
| functions | Implemented | production inventory-value function; deterministic remaining quantity demo | SELECT functions | function returns one value; deterministic/NO SQL attributes must match behavior |
| triggers | Implemented | two production validation triggers; isolated sync/audit triggers | inspect production triggers, run demo schema | trigger runs on data event; broad workflow automation stays in services to avoid hidden logic |
| cursor | Demonstrated | `07_cursor_demo.sql` | CALL procedure and compare set-based query | cursor OPEN/FETCH/handler/CLOSE processes rows; set SQL is generally faster/clearer |
| assertions | Vendor-specific equivalent | MySQL has no CREATE ASSERTION; constraints/triggers/services enforce rules | show CHECK/FK/trigger/service test | never fabricate unsupported syntax |
| sequences | Vendor-specific equivalent | AUTO_INCREMENT used for identities | SHOW CREATE TABLE | MySQL uses AUTO_INCREMENT here rather than standalone CREATE SEQUENCE |
| synonyms | Not natively applicable | MySQL has no CREATE SYNONYM; a demo view shows named abstraction but is not claimed equivalent | create/select/drop demo view | view can provide an alternate query interface, not a full synonym |
| DCL | Demonstrated safely | `12_dcl_roles_privileges.sql` | authorized DBA substitutes local placeholder account names, then SHOW GRANTS | DB privileges protect server objects; application roles protect domain actions—different layers |
| TCL | Implemented/demonstrated | service transactions and `09_transactions_savepoints.sql` | run COMMIT/ROLLBACK/SAVEPOINT example | COMMIT makes work durable; rollback reverses uncommitted work; savepoint marks partial rollback point |

## Unit IV — Transaction management

| Topic | Implemented? | Where and why | How to demonstrate | Viva explanation |
|---|---|---|---|---|
| transaction states and ACID | Implemented/documented | `TRANSACTION_CONCURRENCY_RECOVERY_REPORT.md`, `session_scope()` | walk transfer approval success/failure | active→partially committed→committed or failed→aborted; ACID protects the unit |
| serial/concurrent schedules | Documented | transaction report | draw two allocation schedules | serializability asks whether concurrent conflicts are equivalent to a safe serial order |
| conflict/view serializability | Documented | transaction report | precedence-conflict viva sketch | conflict serializability is practical; view serializability is broader and no analyzer is claimed |
| recoverability | Documented | strict transaction behavior | show rollback on error | dependent transaction should not commit from data that may later abort |
| shared/exclusive and row locks | Implemented/documented | InnoDB, `.with_for_update()` | show repository code and two-tab wait | exclusive row lock serializes competing stock changes |
| dirty/lost/non-repeatable/phantom | Documented with mitigation | READ COMMITTED + locked workflow rows | explain concurrency demo | different anomalies require isolation and explicit locking choices |
| deadlock | Demonstrated safely | stable production lock order + `11_deadlock_demo.sql` | two demo tabs only | InnoDB detects cycle and aborts a victim; retry full transaction if appropriate |
| isolation levels/timestamp ordering | Configuration + theory | READ COMMITTED config; timestamp ordering documented as alternative | inspect connection config | SEMS uses locking; it does not invent a second scheduler |
| log recovery/checkpoint | Documented | recovery section; InnoDB supplies mechanism | demonstrate rollback, not server crash | undo rolls back, redo reapplies committed work, checkpoint bounds recovery |

## Unit V — NoSQL

| Topic | Implemented? | Where and why | How to demonstrate | Viva explanation |
|---|---|---|---|---|
| key-value/document/column/graph models | Optional documented extension | `academic_demo/nosql/README.md` | compare structures | each optimizes a different access/distribution pattern; relational remains correct for SEMS workflows |
| CAP theorem | Documented | same README | partition scenario discussion | under a network partition, distributed systems trade consistency and availability; not “choose any two at all times” |
| MongoDB basic CRUD/projection | Optional demonstration | `mongodb_demo.js`, sanitized JSON | run in a disposable Mongo database if available | documents allow flexible catalogue fields but are not SEMS source of truth |
| replace MySQL | No—intentionally | production requires relational integrity/transactions | show runtime has no Mongo dependency | NoSQL teaching evidence is isolated and optional |

## Assignment 1 — ER/EER

**Implemented:** yes. The authoritative ER/EER is preserved, and `ER_TO_RELATIONAL_MAPPING.md`, `relationships_and_cardinalities.md` and the freeze register explain entities, multivalued attributes, associative entities, roles, min/max cardinality and participation. Demonstrate by tracing each conceptual entity/relationship to a PK/FK/UNIQUE implementation. Viva focus: LAB_CONTACT/USER_PHONE normalize multivalued attributes; REQUEST_ITEM/TRANSFER_ITEM carry relationship attributes.

## Assignment 2 — DDL

**Implemented:** yes. `sql/01_schema.sql` demonstrates CREATE TABLE, PK, FK, UNIQUE, NOT NULL, DEFAULT, CHECK and AUTO_INCREMENT across the complete project. `00_ddl_vendor_equivalents.sql` safely demonstrates ALTER and DROP only in `sems_academic_demo`. Demonstrate with DESCRIBE and SHOW CREATE TABLE. Never confuse this with the smaller five-table coursework database.

## Assignment 3 — DML

**Implemented:** yes. Production seed/application operations and `02_dml_and_advanced_selects.sql` cover INSERT/UPDATE/DELETE/SELECT, equality/range/list/pattern/NULL predicates, DISTINCT, ORDER and LIMIT. Mutating teaching statements use a temporary table. Viva focus: DML is transaction-controlled and validated; lifecycle history is not casually deleted.

## Assignment 4 — Advanced SQL

**Implemented:** yes. `03_joins_aggregates.sql` covers COUNT/SUM/AVG/MIN/MAX, GROUP BY/HAVING and three outer/inner join forms, plus scalar functions. Demonstrate the multi-role transfer join and laboratory summary. A self-join is not forced because no legitimate recursive/peer relationship exists.

## Assignment 5 — Views

**Implemented:** yes. Seven frozen views provide inventory detail, component stock, low stock, request progress, transfer detail, overdue returns and disposal summary. Demonstrate SHOW CREATE VIEW and SELECT from each. Explain grain before aggregation to avoid multiplied totals.

## Assignment 6 — Nested queries

**Implemented:** yes. `04_nested_correlated_queries.sql` contains aggregate and correlated subqueries, IN, EXISTS, NOT EXISTS, a derived table, CTE and window rank. Demonstrate components never requested and positions below their own lab average.

## Assignment 7 — Procedures and functions

**Implemented:** yes. Production includes `sp_component_availability` and `fn_inventory_available_value`; the isolated demo adds IN/OUT/multiple parameters, IF/CASE and deterministic remaining quantity. Demonstrate with CALL and SELECT. Core stock transactions remain in Python services to avoid duplicated logic.

## Assignment 8 — Triggers

**Implemented:** yes. The production schema has exactly two narrow same-lab validation triggers. `08_trigger_audit_demo.sql` shows validation, synchronization and literal audit logging only in the academic schema. Demonstrate the expected invalid quantity or cross-lab failure safely. No audit relation is added to the 13-table production schema.

## Assignment 9 — Cursor

**Demonstrated:** yes, academically isolated. `07_cursor_demo.sql` declares a cursor, opens it, fetches in a loop, handles NOT FOUND, closes it and returns a temporary stock summary. Demonstrate its output followed by the set-based equivalent. Viva focus: cursor proves row-by-row knowledge but the set query is preferred in production.

## Assignment 10 — DBMS mini-project

**Implemented source:** yes. SEMS exceeds the minimum with 13 normalized relations, four real roles, authentication, role/lab scoping, component search, multi-line requests, inter-lab transfer/return, disposal, reports, seven views, constraints, indexes, routines, triggers, transactions, row locks, FastAPI and a modern Next.js frontend. Demonstrate frontend→Python service→SQLAlchemy→MySQL persistence and confirm the write in Workbench.

**Still required before final academic acceptance:** fresh Windows execution against MySQL 8.4.11, safe `sems_test` integration suite, all role workflows, genuine Workbench evidence, responsive/human visual inspection and faculty screenshot capture. These pending local checks are not mislabeled as passed.

