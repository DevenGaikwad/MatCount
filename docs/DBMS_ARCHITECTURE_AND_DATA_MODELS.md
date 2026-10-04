# SEMS DBMS Architecture and Data-Model Study

**Course mapping:** ETCS302 Unit I  
**Production database:** `sems_db`, MySQL Community Server 8.4.11 LTS  
**Schema boundary:** exactly 13 production relations

## Why SEMS requires a DBMS

A DBMS is software that defines, stores, queries, secures and recovers a shared database while enforcing controlled concurrent access. SEMS replaces isolated spreadsheets/registers with one consistent model of laboratories, users, component positions, requests, transfers, returns and disposal. This provides declared keys, referential integrity, transaction atomicity, role-scoped access, reusable queries, backup/recovery support and simultaneous use by multiple departmental actors.

A file-processing solution would duplicate component and laboratory descriptions, depend on application code for every consistency rule, make cross-lab joins difficult, and offer weak protection against two users allocating the same stock. SEMS instead delegates durable state, constraints, locks and recovery to MySQL and keeps role/workflow policy in tested Python services.

## Typical applications and SEMS context

DBMSs support banking, reservations, education, healthcare, logistics and asset control. SEMS is an educational asset-control application: it needs the same core properties—identity, history, consistency, authorization and concurrency—but intentionally avoids enterprise procurement, IoT and ERP scope.

## Three-schema architecture and abstraction

| Level | SEMS realization | What may change independently |
|---|---|---|
| External | Student, Faculty, Lab Assistant and Administrator pages; seven role-scoped report views | UI layout, visible columns and role-specific reports |
| Conceptual | Frozen ER/EER, 13 relational tables, constraints, relationships and workflows | Only through approved baseline change control |
| Internal | InnoDB pages, B-tree indexes, optimizer plans, buffer pool, redo/undo and physical storage | Index/engine implementation without changing user concepts |

**Logical data independence** means presentation queries can evolve while the 13-relation conceptual contract remains stable. **Physical data independence** means an index or storage plan can change without changing table meaning or application workflows. SEMS demonstrates both conservatively: the premium Next.js interface and FastAPI boundary were added without revising the frozen schema, while secondary indexes can be justified or removed through plan evidence.

## DBMS component mapping

| DBMS component | Responsibility | SEMS evidence |
|---|---|---|
| Query processor | Parses SQL, validates names/types, optimizes plans and executes operators | `EXPLAIN`/`EXPLAIN ANALYZE` demonstrations and view queries |
| Storage manager | Manages records, indexes, buffers, files, authorization and transaction storage | MySQL/InnoDB, PK/FK indexes, buffer pool, redo/undo |
| Transaction manager | Provides atomic commit/rollback, locking and recovery | service transaction boundaries and `SELECT ... FOR UPDATE` |
| Authorization/integrity manager | Applies grants and declared constraints | DCL demo, PK/FK/UNIQUE/CHECK, triggers and service RBAC |
| Catalogue | Stores metadata about tables, columns, keys, views and routines | Workbench inspection and `INFORMATION_SCHEMA` queries |

## Data-model comparison

| Model | Structure | Potential SEMS representation | Decision |
|---|---|---|---|
| Hierarchical | Parent–child tree; one parent per child | Department → lab → cabinet → component position | Rejected as canonical because components, requests and transfers participate in multiple relationships that do not form one tree |
| Network | Record graph with navigational owner/member sets | Labs connected by transfers and components | Historically relevant but application queries would be coupled to navigation paths |
| Relational | Typed tables linked by candidate/foreign keys; declarative SQL | The frozen 13 relations and seven views | Selected: best fit for constrained transactions, joins, normalization, ad-hoc reports and ETCS302 learning outcomes |
| Object-oriented | Persistent objects, inheritance and object identity | Component subclasses or rich asset objects | Not required; adds mapping/runtime complexity without improving the MVP facts |
| Document | Self-contained JSON/BSON documents | Flexible component catalogue document | Optional academic example only; duplication and multi-document workflow consistency make it unsuitable as the SEMS source of truth |

The comparison is theoretical evidence, not a reason to force historical models into production.

## Design process used

1. **Requirements analysis:** identify laboratories, people, stock, multi-line requests, transfers, returns, disposal, reports and role boundaries.
2. **Conceptual design:** model strong entities, multivalued attributes, associative entities, cardinalities and participation in the authoritative ER/EER.
3. **Logical design:** map entities and relationships to the frozen 13 relations; select PKs, FKs, UNIQUE and CHECK rules; normalize repeated facts.
4. **Physical design:** choose InnoDB/utf8mb4, indexes, views, limited routines and narrow integrity triggers.
5. **Application design:** expose typed FastAPI adapters over role-aware services and repositories; keep the browser isolated from MySQL credentials.
6. **Validation:** static object-count contract, unit/API tests, safe `_test` integration gate, Workbench verification and human role/visual acceptance.

## ER/EER concepts in SEMS

- **Entities:** LAB, USER, COMPONENT, INVENTORY, COMPONENT_REQUEST, TRANSFER and DISPOSAL_RECORD.
- **Attributes:** simple typed facts such as `lab_name`, `quantity_available`, `request_date` and `transfer_status`.
- **Multivalued attributes:** contacts and phone numbers become LAB_CONTACT and USER_PHONE rather than repeating columns.
- **Associative entities:** REQUEST_ITEM resolves request–component; TRANSFER_ITEM resolves transfer–source-inventory.
- **Relationship roles:** LAB is both transfer source and destination; USER is request creator, transfer creator/receiver and disposal authorizer.
- **Constraints:** keys, domains, referential actions, min/max cardinalities and participation rules are documented in `relationships_and_cardinalities.md` and implemented in `sql/01_schema.sql`.

## Faculty demonstration and viva

Show the architecture diagram in `architecture.md`, then compare an external Student inventory response with the conceptual INVENTORY table and the internal index plan in `academic_demo/sql/05_views_indexes_explain.sql`. A concise viva answer is:

> SEMS uses the relational model because its shared stock workflows require declared relationships, normalized facts, joins, transactions and integrity. The three-schema separation allowed the frontend to modernize without changing the conceptual 13-table database, while indexes may change at the internal level without changing table meaning.

