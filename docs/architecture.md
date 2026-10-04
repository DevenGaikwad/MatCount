# SEMS Application Architecture

## Architectural objective

SEMS uses a compact layered architecture suitable for a strong undergraduate DBMS project. It separates presentation, authorization/business decisions and persistence without introducing enterprise-scale frameworks.

```text
Browser
  → Next.js / React / TypeScript / Tailwind
  → FastAPI route adapter
  → Python service
  → repository
  → SQLAlchemy 2.x
  → PyMySQL
  → MySQL 8.4.11 (`sems_db`)

MySQL Workbench ─────────────────────────────────────────→ same `sems_db`
Preserved Streamlit page → same service/repository stack → same `sems_db`
```

The Next.js application is the canonical presentation layer after modernization. Workbench is an independent SQL client, and Streamlit is a rollback/fallback interface until fresh local parity acceptance. None depends on another being open. Node.js never receives database credentials and never connects to MySQL.

## Layer responsibilities

### Next.js presentation layer

- `frontend/app/` contains login, authenticated shell and ten role-aware route pages.
- `frontend/features/` owns module-specific interaction state; reusable visual primitives stay in `frontend/components/`.
- `frontend/lib/api.ts` is the only HTTP client boundary and attaches an opaque bearer token.
- TypeScript catches client-contract mistakes; Tailwind plus project CSS implements the institutional design system.
- Client code contains no SQL, database driver, credential, business transition or authorization decision.

### FastAPI transport layer

- `api/routes/` validates typed request bodies and delegates to existing Python services.
- `api/dependencies.py` resolves opaque process-local sessions and revalidates the current USER before each operational request.
- `api/errors.py` maps known domain failures to sanitized HTTP responses and logs unexpected failures server-side.
- API routes do not import repositories, SQLAlchemy, PyMySQL or database models.
- CORS origins and trusted hosts are explicit local configuration values.

### Preserved Streamlit fallback

- `app.py` initializes logging/theme, performs login and constructs role-aware navigation.
- `pages/` gathers user input and renders results.
- `ui/` centralizes theme, session identity and reusable visual components.
- Pages do not import repositories, construct SQL or own workflow rules.

### Service layer

- Rechecks database email, active account, role and laboratory scope for actor-aware operations and every write.
- Validates dates, positive quantities, approved quantities and cross-table lab ownership.
- Owns request/transfer/disposal transitions.
- Defines explicit transaction boundaries through `session_scope()`.
- Acquires mutable inventory rows in ascending `inventory_id` order through `SELECT ... FOR UPDATE`.
- Converts predictable domain failures into user-safe exceptions.
- Projects role-sensitive financial/availability rows before API serialization or CSV export; React is never the data-security boundary.

### Repository layer

- Owns ORM statements, parameterized SQL views and row-lock queries.
- Has no Streamlit imports and makes no role or workflow decision.
- Restricts dynamic report-view selection through an allowlist.

### Database layer

- Preserves exactly 13 normalized relations and their PK/FK/UNIQUE/CHECK/domain rules.
- Uses InnoDB and `utf8mb4`.
- Adds justified indexes and seven correctly grained reporting views.
- Uses only two narrow triggers for INVENTORY-to-STORAGE_LOCATION laboratory equality.
- Keeps full workflow automation in Python rather than duplicating it in triggers.

## Authentication and authorization

Credential hashes remain outside the frozen USER relation:

```text
protected bcrypt map → verified email → USER.email
    → account_status → role → lab_id → opaque API session → browser
```

The browser stores only an opaque token in `sessionStorage`; it never receives plaintext passwords, bcrypt hashes or database credentials. Navigation hides irrelevant pages, but service methods independently enforce RBAC. INACTIVE and SUSPENDED users cannot perform operational writes. Sessions are process-local, bounded and expiring, which is appropriate for a single-machine academic deployment and is not presented as distributed enterprise authentication.

## Core transaction boundaries

| Operation | Locked/updated unit |
|---|---|
| Request review | Request header and all request lines |
| Transfer planning | Request header while approved allocation ceilings are checked |
| Transfer approval | Transfer header/lines and all source inventory rows |
| Cancellation | Transfer plus exact reserved source rows |
| Dispatch | Transfer/lines and source rows; reserved quantity only |
| Receipt | Transfer/lines, source identifiers and selected/created destination rows |
| Temporary return | Complete selected temporary lines plus source/destination rows |
| Disposal | Disposal event and one affected inventory row |

Every multi-row operation commits only after all validations/writes succeed and rolls back on exceptions.

Transfer request-quantity review is frozen once allocation begins. Transfer approval/rejection is Administrator-only; Faculty monitors transfers and reviews request quantities. Students cannot call transfer-detail services and see only their own request-progress report.

Financial policy is explicit: Administrator receives global value, Lab Assistant receives own-lab operational cost, and Faculty/Student receive no cost or valuation. Student availability is a smaller allowlisted projection that also removes coordinates and reserved/accounted quantities.

## Frozen-model adaptations

- `TRANSFER_ITEM.inventory_id` always identifies original/source inventory.
- Receipt/return selects destination inventory/location at runtime; it is validated but not persisted as a hidden FK.
- Whole temporary lines are returned. `PARTIALLY_RETURNED` means some temporary lines are complete while others remain, because no frozen quantity-returned attribute exists.
- Demo authentication is external because USER has no password column.
- LAB has no activation/status behavior.

## Presentation boundary

`frontend/app/globals.css`, Tailwind utilities and reusable React components implement the orange/white/maroon academic identity. Original inline SVG icons avoid unlicensed brand assets. The older `.streamlit/config.toml` and `ui/theme.py` remain isolated fallback styling. Either presentation may change without altering database semantics.

## Runtime configuration

The same values control all application connections:

- `DB_HOST`
- `DB_PORT`
- `DB_NAME=sems_db`
- `DB_USER`
- `DB_PASSWORD`

Real secrets stay in `.env` or `.streamlit/secrets.toml`, both Git-ignored.

Only `NEXT_PUBLIC_SEMS_API_URL` is exposed to browser code. API controls use `SEMS_ALLOWED_ORIGINS`, `SEMS_ALLOWED_HOSTS` and `SEMS_API_SESSION_TTL_MINUTES`; none is a database password.

Connection settings are validated before engine creation. The bounded pooled engine uses `pool_pre_ping`, a 30-minute recycle, a short connect timeout and READ COMMITTED isolation. Sessions close in `finally` and roll back on any exception.

## Deployment boundary

The accepted target remains a local Windows/college-laboratory installation. The architecture is modular enough to package cleanly, but public/cloud deployment, distributed session storage, reverse proxies and enterprise identity providers are future operational concerns—not MVP modules.
