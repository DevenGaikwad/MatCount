# SEMS Normalization and Functional Dependency Report

## Scope and claim

SEMS uses atomic fields and separates master, multivalued and transactional facts. Most relations satisfy 3NF and have a defensible BCNF intent under their declared candidate keys. Two frozen operational relations contain controlled semantic redundancy (`inventory.lab_id` and transfer destination derived from the request). This document discloses those dependencies instead of making a blanket, mathematically false BCNF claim.

## 1NF

Every column is scalar: there are no comma-separated contacts, phones, components or allocations. Repeating/multivalued facts are represented by rows:

- LAB contact numbers → `lab_contact`;
- USER phone numbers → `user_phone`;
- request components → `request_item`;
- transfer source allocations → `transfer_item`.

Each relation has an identified primary key, and quantity/date/status values occupy single typed columns.

## 2NF

Relations with single-column surrogate PKs have no partial dependency on a proper subset of that PK. The composite-key relations contain no non-key descriptive attribute:

- `lab_contact(lab_id, contact_number)`;
- `user_phone(user_id, phone_number)`.

Associative lines use surrogate PKs for stable references, while their natural pairs are UNIQUE. All line-specific attributes depend on the complete association represented by that line, not only on the parent ID.

## Principal functional dependencies

| Relation | Important functional dependencies / candidate keys | Assessment |
|---|---|---|
| LAB | `lab_id → name, department, building, type`; `(lab_name, department_name) → remaining attributes` | 3NF; BCNF under declared UNIQUE meaning |
| LAB_CONTACT | `(lab_id, contact_number)` is the only key and fact | BCNF |
| USER | `user_id → lab_id, full_name, email, role, status`; `email → user row` | 3NF/BCNF under UNIQUE email |
| USER_PHONE | `(user_id, phone_number)` is the only key and fact | BCNF |
| COMPONENT_CATEGORY | `category_id → name, description`; `category_name → category row` | 3NF/BCNF |
| COMPONENT | `component_id → all descriptive attributes`; non-NULL `part_number → component row` | 3NF; BCNF intent, noting SQL permits multiple NULL part numbers |
| STORAGE_LOCATION | `storage_location_id → lab and coordinates`; full coordinate tuple intends uniqueness | 3NF by surrogate key; BCNF intent is qualified because nullable UNIQUE columns do not form a strict SQL candidate key for rows containing NULL |
| INVENTORY | `inventory_id → lab, component, location, quantities, cost, status, timestamp`; declared `(lab_id, component_id, storage_location_id)` identifies a row | Controlled exception described below |
| COMPONENT_REQUEST | `request_id → requesting lab, creator, dates, priority, reason, status` | 3NF/BCNF by declared structure |
| REQUEST_ITEM | `request_item_id → request, component, quantities, state, remarks`; `(request_id, component_id) → line` | 3NF/BCNF by declared keys |
| TRANSFER | `transfer_id → request, source/destination, users, dates and states` | Controlled workflow dependency described below |
| TRANSFER_ITEM | `transfer_item_id → transfer, source inventory, quantities, dates, conditions`; `(transfer_id, inventory_id) → line` | 3NF/BCNF by declared keys |
| DISPOSAL_RECORD | `disposal_id → inventory, authorizer, quantity, date, reason, method, remarks` | 3NF/BCNF by declared structure |

## Complete key and non-key dependency catalogue

Notation: `{A,B}` is a composite determinant; `→` is a functional dependency. Candidate keys are stated under the SQL NULL semantics actually enforced by the schema, so nullable UNIQUE declarations are qualified rather than overstated.

| Relation | Primary key | Other candidate key(s) | Non-key dependency on determinant | Normal-form conclusion |
|---|---|---|---|---|
| LAB | `lab_id` | `{lab_name, department_name}` | each key → `building_name, lab_type` and the other identifier attributes | BCNF under the declared uniqueness/business meaning |
| LAB_CONTACT | `{lab_id, contact_number}` | none | no non-key attributes | BCNF |
| USER | `user_id` | `email` | each key → `lab_id, full_name, role, account_status` | BCNF under UNIQUE non-null email |
| USER_PHONE | `{user_id, phone_number}` | none | no non-key attributes | BCNF |
| COMPONENT_CATEGORY | `category_id` | `category_name` | each key → `description` and the other identifier | BCNF |
| COMPONENT | `component_id` | non-null `part_number` | `component_id` → `category_id, component_name, part_number, specification, unit_of_measure, minimum_stock_level, manufacturer_details` | 3NF/BCNF intent; multiple NULL part numbers are not a candidate key |
| STORAGE_LOCATION | `storage_location_id` | full non-null coordinate tuple only in the business interpretation | PK → `lab_id, cabinet_no, shelf_no, drawer_no, location_type` | 3NF/BCNF intent; nullable coordinate fields qualify the SQL candidate-key claim |
| INVENTORY | `inventory_id` | `{lab_id, component_id, storage_location_id}` | either declared row key → quantities, cost, status, timestamp; semantic `storage_location_id → lab_id` also holds | controlled 3NF/BCNF exception disclosed below |
| COMPONENT_REQUEST | `request_id` | none | PK → `requesting_lab_id, created_by, request_date, required_by_date, priority, reason, request_status` | BCNF by declared structure |
| REQUEST_ITEM | `request_item_id` | `{request_id, component_id}` | either key → `quantity_requested, quantity_approved, item_status, remarks` | BCNF; association attributes depend on the complete logical line |
| TRANSFER | `transfer_id` | none | PK → request/source/destination/users/dates/statuses; valid workflow also implies `request_id → destination_lab_id` for SEMS transfers | controlled dependency disclosed below |
| TRANSFER_ITEM | `transfer_item_id` | `{transfer_id, inventory_id}` | either key → sent/received quantities, due/return dates and conditions | BCNF; allocation facts depend on the complete logical line |
| DISPOSAL_RECORD | `disposal_id` | none | PK → `inventory_id, authorized_by, quantity_disposed, disposal_date, disposal_reason, disposal_method, remarks` | BCNF by declared structure |

## Multivalued dependencies and Fourth-Normal-Form reasoning

Conceptually, a laboratory can have independent contact numbers (`lab_id ↠ contact_number`) and a user can have independent phone numbers (`user_id ↠ phone_number`). Keeping these values in LAB or USER would create repeating groups, arbitrary numbered columns or cross-products with other independent facts. LAB_CONTACT and USER_PHONE isolate each multivalued dependency into a two-attribute relation. Both relations have the whole row as a key, so the decomposition is compatible with 4NF reasoning even though ETCS302 requires proof principally through 3NF/BCNF.

REQUEST_ITEM and TRANSFER_ITEM are not multivalued text fields. They are associative relations whose non-key facts—quantities, statuses, dates and conditions—describe a particular parent/target association. Separating them removes repeating request/transfer columns and header duplication.

## Domain and referential constraints supporting normalization

- unsigned integer/decimal domains and CHECK rules prevent negative stock/cost and invalid quantity comparisons;
- ENUM domains constrain roles and lifecycle states to the frozen vocabulary;
- date checks preserve required-by, dispatch/receipt and return ordering where representable;
- NOT NULL distinguishes mandatory participation from genuinely unknown/later facts;
- UNIQUE rules enforce alternate row identities and prevent duplicate association lines;
- FKs prevent orphan contacts, phones, stock positions, request lines, transfer lines and disposal events;
- controlled CASCADE exists only for owned multivalued/line relations; master/history relationships use RESTRICT where deletion would lose meaning.

## Controlled frozen-model dependencies

### INVENTORY lab ownership

Because every STORAGE_LOCATION belongs to one LAB, the enforced semantic dependency `storage_location_id → lab_id` also holds in INVENTORY. Therefore `inventory.lab_id` is derivable and strict BCNF—and, under that semantic FD, strict 3NF—is not claimed for this relation.

The frozen model nevertheless retains the direct LAB–INVENTORY relationship for ownership, lab-scoped queries and the validated ER mapping. The database triggers and service checks enforce equality between INVENTORY.lab_id and the location's lab, preventing contradictory updates. This is a small, documented, integrity-protected denormalization—not an unnoticed anomaly and not permission to redesign the schema.

### TRANSFER destination

The service requires TRANSFER.destination_lab_id to equal its COMPONENT_REQUEST.requesting_lab_id. Thus the workflow creates a semantic dependency from `request_id` to destination lab across valid transfer rows. The direct destination FK is retained because the frozen ER/EER explicitly models LAB receives TRANSFER and because it makes each transfer operationally self-describing. Service validation prevents disagreement.

## Why the associative/normalized relations exist

- `request_item` resolves the M:N conceptual relationship between COMPONENT_REQUEST and COMPONENT. Requested/approved quantities, item state and remarks belong to the association.
- `transfer_item` resolves the M:N relationship between TRANSFER and source INVENTORY. Sent/received quantities, return dates and conditions belong to the allocation.
- `lab_contact` and `user_phone` implement multivalued attributes without repeating groups or arbitrary `phone_1`, `phone_2` columns.
- `inventory` represents an operational lab–component–storage position with free/reserved quantities, cost and state. It prevents copying component descriptions and storage coordinates into every stock event.

## Anomaly reduction

- Category/component/lab/location descriptions are updated once in master relations.
- Adding a phone/contact adds a row rather than changing table structure.
- A request or transfer can gain multiple lines without duplicating its header facts.
- FKs prevent orphan lines/events; UNIQUE rules prevent duplicate logical lines/positions.
- Disposal facts remain historical rows instead of being overwritten into INVENTORY.
- View grains explicitly prevent report joins from multiplying totals.

## Defensible viva statement

“SEMS is normalized to a strong 3NF design overall, with normalized multivalued and associative relations. I do not claim universal BCNF. The frozen INVENTORY relation carries a controlled lab-ownership redundancy implied by STORAGE_LOCATION, and TRANSFER repeats the request destination role; both are explicitly validated. This is more accurate than ignoring semantic dependencies.”
