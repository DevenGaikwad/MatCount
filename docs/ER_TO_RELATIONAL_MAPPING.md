# SEMS ER/EER to Relational Mapping

## Entity mapping

The frozen conceptual model maps 11 principal entities plus two relations produced from multivalued attributes. Every entity with a surrogate identifier maps to one base relation; LAB_CONTACT and USER_PHONE use owner/value composite keys. REQUEST_ITEM and TRANSFER_ITEM are associative entities carrying relationship attributes.

## Validated relationship traceability

`1` denotes exactly one; `0..1` optional one; `0..N` optional many; operational minimum participation is enforced by services where a DRAFT parent may temporarily have no line.

| Conceptual relationship | Relational implementation | Cardinality and participation | Implementation rule |
|---|---|---|---|
| LAB has CONTACT | `lab_contact.lab_id → lab.lab_id` | LAB `0..N`; contact `1` LAB | Composite PK prevents duplicate number per lab; owner deletion cascades |
| LAB employs USER | ``user.lab_id → lab.lab_id`` | LAB `0..N`; USER exactly `1` LAB | User lab is mandatory; lab deletion restricted while users exist |
| USER has PHONE | `user_phone.user_id → user.user_id` | USER `0..N`; phone row exactly `1` USER | Composite PK normalizes the multivalued attribute |
| LAB contains STORAGE_LOCATION | `storage_location.lab_id → lab.lab_id` | LAB `0..N`; location exactly `1` LAB | Location ownership mandatory; delete restricted |
| COMPONENT_CATEGORY classifies COMPONENT | `component.category_id → component_category.category_id` | Category `0..N`; component exactly `1` category | Category deletion restricted while components exist |
| COMPONENT appears in INVENTORY | `inventory.component_id → component.component_id` | Component `0..N`; inventory row exactly `1` component | Stock carries FK, not copied catalogue details |
| STORAGE_LOCATION stores INVENTORY | `inventory.storage_location_id → storage_location.storage_location_id` | Location `0..N`; inventory row exactly `1` location | UNIQUE lab/component/location position |
| LAB maintains INVENTORY | `inventory.lab_id → lab.lab_id` | LAB `0..N`; inventory row exactly `1` LAB | Trigger/service require location lab = inventory lab |
| LAB raises COMPONENT_REQUEST | `component_request.requesting_lab_id → lab.lab_id` | LAB `0..N`; request exactly `1` requesting LAB | Mandatory even while request is DRAFT |
| USER creates COMPONENT_REQUEST | `component_request.created_by → user.user_id` | USER `0..N`; request exactly `1` creator | Creator identity immutable in normal workflow |
| COMPONENT_REQUEST includes REQUEST_ITEM | `request_item.request_id → component_request.request_id` | DRAFT request `0..N`, submitted request operationally `1..N`; item exactly `1` request | Submission rejects an empty request; line deletion follows header cascade |
| COMPONENT is requested as REQUEST_ITEM | `request_item.component_id → component.component_id` | COMPONENT `0..N`; item exactly `1` component | UNIQUE `(request_id, component_id)` prevents duplicate component line |
| USER submits/creates TRANSFER | `transfer.created_by → user.user_id` | USER `0..N`; transfer exactly `1` creator | Service permits Lab Assistant/Administrator planning |
| USER receives TRANSFER | `transfer.received_by → user.user_id` | USER `0..N`; transfer `0..1` before/at receipt | Nullable until all lines received; paired with received_date |
| LAB sends TRANSFER | `transfer.source_lab_id → lab.lab_id` | LAB `0..N`; transfer exactly `1` source | Source owns every allocated source INVENTORY row |
| LAB receives TRANSFER | `transfer.destination_lab_id → lab.lab_id` | LAB `0..N`; transfer exactly `1` destination | Destination equals requesting lab and differs from source |
| COMPONENT_REQUEST is fulfilled by TRANSFER | `transfer.request_id → component_request.request_id` | Request `0..N`; transfer exactly `1` request | Only approved demand may be allocated; cumulative allocations cannot exceed approval |
| TRANSFER contains TRANSFER_ITEM | `transfer_item.transfer_id → transfer.transfer_id` | DRAFT transfer `0..N`, approved/dispatchable transfer operationally `1..N`; item exactly `1` transfer | Approval rejects empty transfer; line follows transfer cascade |
| INVENTORY is allocated to TRANSFER_ITEM | `transfer_item.inventory_id → inventory.inventory_id` | Inventory `0..N`; item exactly `1` source inventory | UNIQUE `(transfer_id, inventory_id)`; original/source row retained |
| INVENTORY is disposed through DISPOSAL_RECORD | `disposal_record.inventory_id → inventory.inventory_id` | Inventory `0..N`; disposal exactly `1` inventory | History restricts inventory deletion; quantity is positive and stock-checked |
| USER authorizes DISPOSAL_RECORD | `disposal_record.authorized_by → user.user_id` | USER `0..N`; disposal exactly `1` authorizer | Administrator role is revalidated in service |

## Important EER roles and constraints

- LAB plays distinct `source` and `destination` roles in TRANSFER; `source_lab_id <> destination_lab_id` is a database CHECK and a service rule.
- USER plays `created_by`, `received_by` and `authorized_by` roles in different lifecycle relations. No nonexistent `approved_by` FK is claimed.
- TRANSFER_ITEM.inventory_id denotes original/source inventory only. Destination selection is validated during receipt/return but is not persisted because the frozen relation has no destination FK.
- Parent minimum participation is conditional: DRAFT headers may exist temporarily without lines, while submission/approval gates enforce at least one line.

## Relational mapping rules demonstrated

- Strong entity → table with surrogate PK.
- 1:N → FK on the N side.
- Multivalued attribute → separate owner/value relation with composite PK.
- M:N with attributes → associative entity (`request_item`, `transfer_item`).
- Optional role participation → nullable FK (`received_by`).
- Repeated role relationship → separate named FKs (`source_lab_id`, `destination_lab_id`).
