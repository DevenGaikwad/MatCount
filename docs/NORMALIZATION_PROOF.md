# SEMS normalization and functional-dependency review

Updated 11 October 2026. This replaces the earlier surrogate-key-only 2NF explanation. The installed 13-relation physical schema remains operational; logical alternatives are proposals, not a deployed migration.

## Definitions and 1NF

A functional dependency must hold in all valid states. A candidate key is minimal; prime attributes belong to a candidate key. 2NF checks every candidate key for partial dependence of a non-prime attribute. 3NF requires a superkey determinant or a prime dependent attribute for each non-trivial FD. Contacts, phones, request lines and transfer allocations are separate rows/relations, with no repeating column groups.

## All thirteen relations

| Relation | Identifiers | Principal dependencies | Assessment |
|---|---|---|---|
| LAB | lab_id; (lab_name, department_name) | Each key -> lab descriptors | 3NF under stated lab facts |
| LAB_CONTACT | (lab_id, contact_number) | Whole pair identifies a contact row; no non-prime attribute | 3NF; independent multivalued fact |
| USER | user_id; email | Each key -> lab_id, full_name, role, account_status | 3NF; no FD from lab to user role/name |
| USER_PHONE | (user_id, phone_number) | Whole pair identifies a phone row; no non-prime attribute | 3NF; independent multivalued fact |
| COMPONENT_CATEGORY | category_id; category_name | Each key -> description and category facts | 3NF under category semantics |
| COMPONENT | component_id | component_id -> catalogue facts; populated part_number is conditionally unique | 3NF under stated FDs; NULL part numbers are not universal keys |
| STORAGE_LOCATION | storage_location_id | ID -> lab and coordinate facts; full non-NULL coordinate tuple is conditionally unique | 3NF under stated FDs; nullable coordinate UNIQUE is qualified |
| INVENTORY | inventory_id; implied (component_id, storage_location_id) | storage_location_id -> lab_id; whole stock-position key -> balance/cost/state | Controlled exception; 2NF and 3NF fail under ownership FD |
| COMPONENT_REQUEST | request_id | request_id -> header facts | 3NF; admin can create for another lab, so creator -> requesting lab is not universal |
| REQUEST_ITEM | request_item_id; (request_id, component_id) | Each complete key -> requested/approved/state/remarks | 3NF; approval differs by request-component pair |
| TRANSFER | transfer_id | transfer_id -> movement facts; request_id -> destination_lab_id for valid workflow | Controlled 3NF exception; request_id can identify several transfers |
| TRANSFER_ITEM | transfer_item_id; (transfer_id, inventory_id) | Each complete key -> sent/received/return/condition facts | 3NF under line semantics |
| DISPOSAL_RECORD | disposal_id | disposal_id -> inventory, authorizer, quantity/date/reason/method | 3NF under event semantics |

## Composite associations

`lab_contact` and `user_phone` contain only their composite-key attributes. Request decisions depend on the full request/component pair, and transfer quantities/conditions depend on the full transfer/inventory pair. These statements concern business meaning, not accidental uniqueness in a small dataset.

## Inventory: strict 2NF and 3NF exception

Let I=inventory_id, C=component_id, S=storage_location_id and L=lab_id. I determines the full row; the declared position UNIQUE tuple is (L,C,S). Ownership gives S→L. The closure (C,S)+ obtains L and then I, so (C,S) is an implied minimal candidate key. L is non-prime and depends on proper subset S of that key. A surrogate I does not remove this partial dependency.

Decompose into LOCATION(S,L,coordinates) and STOCK(I,C,S,available,reserved,cost,status,time), with UNIQUE(C,S). Intersection S is a key of LOCATION, so the join is lossless for valid stock rows. I survives as the reference for allocations/disposal. S→L and the stock identifiers are preserved in their projected relations.

## Transfer: strict 3NF exception

Let T=transfer_id, Q=request_id and D=destination_lab_id. A valid workflow requires D to match the request laboratory, giving Q→D. Q is not a transfer superkey because a request can be served by multiple transfers; D is non-prime.

Decompose into REQUEST(Q,D,header facts) and MOVEMENT(T,Q,source,users,dates,state,approval). Intersection Q is the REQUEST key, giving a lossless join. T remains the movement key and Q→D is represented once in REQUEST.

## Protection, anomalies and qualifications

- Child inventory INSERT/UPDATE triggers validate same-lab ownership. They do not independently guard all direct parent-location ownership reassignment.
- Transfer services validate request destination and lifecycle states. Direct administrative changes to request laboratory still require dependency review.
- Nullable part_number and nullable shelf/drawer coordinate UNIQUE declarations are conditional identifiers, not unconditional relational candidate keys.
- created_by does not universally determine requesting_lab_id: Administrators can create requests for another lab.
- Inventory status is not solely a function of quantity because BLOCKED/INACTIVE overrides exist.

## Experiment and migration boundary

A temporary-relation experiment on the isolated MySQL 8.4.11 review fixture reconstructed 39 inventory and 3 transfer rows with zero mismatches. Source rows were not changed. The concrete experiment checks the fixture; the key/intersection reasoning supplies the formal valid-state argument. Temporary tables do not claim full FK enforcement or transparent ORM compatibility.

A physical migration must modify ORM models, joins, role projections, services, constraints/triggers, views and API tests while preserving keys/history. Do not perform it immediately before evaluation. The live stock expansion is separate: it adds catalogue/position data, not a normalization migration.

## Reference

[SFU CMPT 354: formal Third Normal Form and decomposition](https://www2.cs.sfu.ca/CourseCentral/354/zaiane/material/notes/Chapter7/node11.html). The dependency/key conclusions above come from the actual project schema and services.
