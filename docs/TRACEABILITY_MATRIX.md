# SEMS Requirement → Implementation → Test Traceability

| Requirement / rule | Database relation | SQL constraint/view | Service/API | Canonical Next.js route (Streamlit fallback) | Test(s) | Status |
|---|---|---|---|---|---|---|
| Exactly 13 full-project relations | All | `01_schema.sql`; SQL validator | — | — | `test_sql_contract`, `test_models_contract` | Implemented; runtime pending |
| External secure login mapped by email | USER | UNIQUE email; no password column | `auth_service`; `/api/auth/*` | `/login` (`app.py`) | auth/security/API session tests | Implemented; source runtime PASS |
| ACTIVE role/lab identity revalidated | USER | account-status ENUM | `rbac`, `auth_service` | app shell | `test_rbac`, `test_service_security` | Implemented |
| Multivalued contacts/phones | LAB_CONTACT, USER_PHONE | Composite PK/FK CASCADE | `master_data_service` | Laboratories, Users | model/schema contracts | Implemented |
| Null-normalized storage uniqueness | STORAGE_LOCATION | UNIQUE coordinate (NULL caveat) | `master_data_service` | Storage Locations | `test_master_data_service` | Implemented |
| Same-lab inventory/location | INVENTORY, STORAGE_LOCATION | FK + two triggers | `inventory_service` | Inventory | MySQL constraints/academic features | Implemented; runtime pending |
| Cross-lab availability search | INVENTORY + masters | `v_inventory_detail` | `analytics_service`; `/api/inventory` | `/inventory` (Inventory) | analytics/SQL/API architecture | Implemented |
| Nonnegative stock and correct status | INVENTORY, COMPONENT | CHECKs; low-stock views | inventory/transfer/disposal services | Inventory | `test_rules`, MySQL constraints | Implemented |
| On-hand valuation includes reserved | INVENTORY | `inventory_value` in views; verification query | analytics/report repository | Dashboard, Reports | SQL contract + MySQL academic features | Implemented |
| Multi-line request creation | COMPONENT_REQUEST, REQUEST_ITEM | UNIQUE line; positive requested CHECK | `request_service.create_draft` | Component Requests | rules/request/model contracts | Implemented |
| Empty request cannot submit | COMPONENT_REQUEST, REQUEST_ITEM | Operational participation gate | `submit_request` | Component Requests | workflow contract/manual acceptance | Implemented |
| Partial/full/rejected review | REQUEST_ITEM | approval-range CHECK; request view | `review_request` | Component Requests | `test_rules`, seed/integration | Implemented |
| No backward approval revision after allocation | REQUEST_ITEM, TRANSFER_ITEM | allocation joins | `review_request` | Component Requests | workflow contract | Implemented |
| Request cancellation before approval | COMPONENT_REQUEST | frozen CANCELLED state | `cancel_request` | Component Requests | `test_request_service` | Implemented |
| Request-linked transfer planning | TRANSFER, TRANSFER_ITEM | FKs, UNIQUE allocation, distinct-lab CHECK | transfer service + approved-plan read; `/api/transfers` | `/transfers` (Transfers) | workflow/SQL/service-security/API contracts | Implemented |
| Administrator transfer approval | TRANSFER | approval/status ENUMs | `approve_transfer`, `reject_transfer` | Transfers | `test_service_security` | Implemented |
| Reservation Q: available−Q, reserved+Q | INVENTORY | nonnegative CHECK | `approve_transfer` + `reserve_stock` | Transfers | `test_rules` | Implemented |
| Cancellation releases reservation | INVENTORY, TRANSFER | state domain | `cancel_transfer` + `release_reservation` | Transfers | `test_rules` | Implemented |
| Dispatch reduces reserved only | INVENTORY, TRANSFER_ITEM | quantity/state domains | `dispatch_transfer` | Transfers | `test_rules`, workflow contract | Implemented |
| Issue condition written at dispatch | TRANSFER_ITEM | nullable condition column | `dispatch_transfer` | Transfers | workflow contract | Implemented |
| Receipt uses explicit destination selection | INVENTORY, TRANSFER_ITEM | no destination FK by design | `receive_transfer` | Transfers | workflow contract/manual acceptance | Implemented |
| Partial receipt is cumulative and bounded | TRANSFER_ITEM | `received <= sent` CHECK | `receive_transfer` | Transfers | MySQL constraints/manual acceptance | Implemented |
| Whole-line temporary return | TRANSFER_ITEM, INVENTORY | due/return CHECK; overdue view | `return_temporary_items` | Transfers | rules/workflow contract | Implemented |
| Return condition only at actual return | TRANSFER_ITEM | nullable condition column | `return_temporary_items` | Transfers | workflow contract | Implemented |
| Administrator-only disposal | DISPOSAL_RECORD, INVENTORY | positive CHECK; RESTRICT history FKs | `disposal_service` | Disposal | RBAC/rules/MySQL tests | Implemented |
| Seven correctly grained reports | All workflow relations | seven views | `analytics_service` | Dashboard, Reports | SQL/integration tests | Implemented; runtime pending |
| Student sees own request progress | COMPONENT_REQUEST | `v_request_progress` + creator filter | analytics/report repository | Reports | service security/source audit | Implemented |
| CSV export and spreadsheet safety | View results | — | `analytics_service.to_csv` | Inventory, Reports | `test_analytics` | Implemented |
| Atomic multi-row failure rollback | Inventory/workflow relations | InnoDB | `session_scope`; stock services | Workflow pages | `test_transactions`; local integration | Implemented; MySQL proof pending |
| Workbench ↔ professional frontend same DB | All | `SELECT DATABASE()`; `07` | settings/engine; FastAPI | all routes | final acceptance + Workbench proof | Prepared; fresh local proof pending |
| Browser never connects directly to MySQL | — | — | API routes delegate to services | all Next.js routes | architecture + secret scan | Implemented; static PASS |
| Professional frontend technical gate | — | — | typed API contracts | login/shell/all 10 modules | TypeScript, ESLint, Vitest, Next build | Implemented; technical PASS |
| One-command non-destructive acceptance | All | read-only live object checks | validation scripts | — | `final_acceptance.ps1` | Created; fresh Windows run pending |

“Runtime pending” means the artifact exists and static checks pass, but the corresponding statement has not been freshly executed against the user's MySQL 8.4.11 environment after modernization.
