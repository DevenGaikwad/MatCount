# SEMS Relationships and Cardinalities

This document describes the implemented relational mapping. It does not replace or redesign the frozen ER/EER.

| Relationship | Cardinality | Child participation | FK implementation |
|---|---:|---|---|
| LAB employs USER | 1:N | USER exactly one LAB | `user.lab_id` |
| LAB owns LAB_CONTACT | 1:N | Contact exactly one LAB | `lab_contact.lab_id` |
| USER owns USER_PHONE | 1:N | Phone exactly one USER | `user_phone.user_id` |
| COMPONENT_CATEGORY classifies COMPONENT | 1:N | Component exactly one category | `component.category_id` |
| LAB contains STORAGE_LOCATION | 1:N | Location exactly one LAB | `storage_location.lab_id` |
| LAB maintains INVENTORY | 1:N | Inventory exactly one LAB | `inventory.lab_id` |
| COMPONENT appears in INVENTORY | 1:N | Inventory exactly one component | `inventory.component_id` |
| STORAGE_LOCATION stores INVENTORY | 1:N | Inventory exactly one location | `inventory.storage_location_id` |
| LAB raises COMPONENT_REQUEST | 1:N | Request exactly one requesting LAB | `component_request.requesting_lab_id` |
| USER creates COMPONENT_REQUEST | 1:N | Request exactly one creator | `component_request.created_by` |
| COMPONENT_REQUEST contains REQUEST_ITEM | 1:N | Submitted request requires one or more items | `request_item.request_id` |
| COMPONENT appears in REQUEST_ITEM | 1:N | Item exactly one component | `request_item.component_id` |
| COMPONENT_REQUEST is fulfilled by TRANSFER | 1:N | Transfer exactly one request | `transfer.request_id` |
| LAB sends TRANSFER | 1:N | Transfer exactly one source LAB | `transfer.source_lab_id` |
| LAB receives TRANSFER | 1:N | Transfer exactly one destination LAB | `transfer.destination_lab_id` |
| USER creates TRANSFER | 1:N | Transfer exactly one creator | `transfer.created_by` |
| USER confirms receipt | 1:N | Transfer zero/one receiver until receipt | `transfer.received_by` nullable |
| TRANSFER contains TRANSFER_ITEM | 1:N | Operational transfer requires one or more items | `transfer_item.transfer_id` |
| INVENTORY is allocated through TRANSFER_ITEM | 1:N over time | Item exactly one source inventory | `transfer_item.inventory_id` |
| INVENTORY has DISPOSAL_RECORD events | 1:N | Disposal exactly one inventory row | `disposal_record.inventory_id` |
| USER authorizes DISPOSAL_RECORD | 1:N | Disposal exactly one authorizer | `disposal_record.authorized_by` |

## Associative/normalizing relations

- `REQUEST_ITEM` resolves the request-to-component conceptual M:N relationship.
- `TRANSFER_ITEM` resolves the transfer-to-source-inventory conceptual M:N relationship.
- `INVENTORY` represents the operational component-at-location association with laboratory ownership.
- `LAB_CONTACT` and `USER_PHONE` normalize multivalued attributes into 1NF relations.

Because STORAGE_LOCATION already determines its LAB, the frozen direct `inventory.lab_id` is a controlled semantic redundancy. The same-lab triggers and service validation prevent disagreement; `NORMALIZATION_PROOF.md` does not falsely claim universal BCNF.

## Referential actions

- CASCADE delete is limited to true owned dependents: LAB_CONTACT and USER_PHONE, plus controlled pre-operational request/transfer line ownership.
- RESTRICT protects masters, inventory and lifecycle history.
- All identifier FKs use ON UPDATE CASCADE.
- Services prevent deletion of operational headers even where owned-line cascade is declared.

## Important non-relationships

- No direct TRANSFER-to-DISPOSAL_RECORD relationship.
- No destination-inventory FK in TRANSFER_ITEM.
- No password/authentication FK or table.
- No LAB status relation/attribute.
- No procurement, maintenance, QR, audit-log, AI or IoT relation.
