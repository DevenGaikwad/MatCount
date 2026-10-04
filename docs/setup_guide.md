# SEMS Windows and VS Code Setup Guide

## 1. Install prerequisites

Install and verify:

- MySQL Community Server 8.4.11 LTS.
- MySQL Workbench.
- Python 3.12 or later.
- Node.js 20.9 or later (Node.js 24 recommended).
- VS Code with the Microsoft Python extension.

Open Command Prompt:

```cmd
mysql --version
py -3.12 --version
node --version
npm --version
```

If `mysql` is not on PATH, that does not prevent Workbench execution, but note the MySQL installation path for CLI use.

## 2. Build `sems_db` in Workbench

1. Start the Windows MySQL service.
2. Open the local Workbench connection.
3. Execute `SELECT VERSION();` and confirm 8.4.11.
4. Run complete scripts `00` through `06` in numeric order.
5. Refresh SCHEMAS and verify all 13 relations.
6. Run `07_verification_queries.sql`.

Detailed steps: `docs/MYSQL_WORKBENCH_EXECUTION_GUIDE.md`.

## 3. Create a least-privilege application account

As a MySQL administrator, choose a strong local password and run:

```sql
CREATE USER IF NOT EXISTS 'sems_app'@'localhost'
  IDENTIFIED BY 'YOUR_STRONG_LOCAL_PASSWORD';
GRANT SELECT, INSERT, UPDATE, DELETE, EXECUTE
  ON sems_db.* TO 'sems_app'@'localhost';
FLUSH PRIVILEGES;
```

Do not paste the real password into project files or screenshots.

## 4. Prepare Python

Open the project folder in VS Code, then run:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Select `.venv\Scripts\python.exe` as the VS Code interpreter.

Install the locked frontend packages:

```powershell
Set-Location frontend
npm ci
Set-Location ..
```

## 5. Configure secrets

Choose one method.

### `.env`

Copy `.env.example` to `.env` and replace placeholders:

```text
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=sems_db
DB_USER=sems_app
DB_PASSWORD=your-local-password
```

### Streamlit secrets

Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and replace placeholders. Do not configure both methods with conflicting values; environment variables take precedence.

## 6. Configure demo login hashes

Run:

```powershell
python scripts/generate_demo_hash.py
```

Generate hashes for the desired seeded emails and place them in the selected protected configuration. Hashes are not stored in USER.

## 7. Configure the browser/API boundary

Copy `frontend/.env.local.example` to `frontend/.env.local` if the API will not use the default `http://127.0.0.1:8000/api`. This file may contain only a non-sensitive API URL:

```text
NEXT_PUBLIC_SEMS_API_URL=http://127.0.0.1:8000/api
```

Do not put DB_HOST, DB_USER, DB_PASSWORD, database URLs, bcrypt hashes or login passwords in any `NEXT_PUBLIC_*` variable.

## 8. Start and verify the professional interface

Run the non-destructive readiness check first:

```powershell
python scripts/preflight_check.py
```

It checks Python, required files, imports, safe configuration and—when credentials are complete—a short MySQL identity/health query. It never prints the password.

In terminal 1:

```powershell
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

In terminal 2:

```powershell
Set-Location frontend
npm run dev
```

Open `http://127.0.0.1:3000`. API documentation is available locally at `http://127.0.0.1:8000/api/docs` for technical inspection; it is not a replacement for the UI.

Expected behavior:

- The unauthenticated view shows only the professional login.
- The health indicator reflects the API/database state without displaying credentials.
- A valid external demo credential maps to an ACTIVE seeded USER.
- Sidebar navigation, role badge, laboratory context and actions change by role.

### Preserved Streamlit fallback

Until fresh local parity acceptance and explicit user approval, the known-good fallback remains:

```powershell
streamlit run app.py
```

## 9. Run the canonical acceptance

After configuring `sems_db` and a dedicated `sems_test` URL, use one command from the project root:

```powershell
.\scripts\final_acceptance.ps1
```

The complete command is non-destructive to `sems_db`. It restores missing frontend packages with `npm ci`, then validates runtimes/structure, Python/SQL/ETCS302 demo contracts, live database objects, `_test` safety, full pytest/API, frontend type-check/lint/test/build, secret hygiene, Python dependency consistency and the npm critical-vulnerability audit. It writes a sanitized local log under `logs/`.

Optional developer scopes exist:

```powershell
.\scripts\final_acceptance.ps1 -Fast
.\scripts\final_acceptance.ps1 -FrontendOnly
.\scripts\final_acceptance.ps1 -BackendOnly
```

Only the normal command is the complete release gate.

### Optional ETCS302 teaching evidence

The application does not require the academic demo schema. After `sems_db` is verified, follow the safety/order table in `academic_demo/README.md` and `docs/MYSQL_WORKBENCH_EXECUTION_GUIDE.md`. Never copy the demo audit table, cursor output table or concurrency rows into `sems_db`; they belong only to `sems_academic_demo`. MongoDB material under `academic_demo/nosql/` is optional and requires no production configuration.

## 10. Lower-level test commands

Combined server-independent validation:

```powershell
python scripts/validate_project.py
```

```powershell
pytest -m "not integration"
```

For MySQL integration tests, first build a dedicated test database:

```powershell
$env:DB_PASSWORD = "LOCAL_TEST_ADMIN_PASSWORD"
python scripts/build_database.py --database sems_test --user root
$env:SEMS_TEST_DATABASE_URL = "mysql+pymysql://root:URL_ENCODED_PASSWORD@127.0.0.1:3306/sems_test?charset=utf8mb4"
pytest
```

The build utility accepts only `sems_db` or a name ending `_test`. Integration fixtures refuse other database names.

The older Python-only strict gate remains useful for diagnosis:

```powershell
python scripts/validate_project.py --local-acceptance
```

## 11. Safe development reset

Back up valued data, then in one Workbench connection:

```sql
SET @sems_reset_confirmation = 'RESET_SEMS_DB';
```

Run `sql/99_reset_database.sql`, followed by scripts `00` through `06`. The reset script targets only `sems_db` and refuses execution without exact confirmation.

## 12. Troubleshooting

| Symptom | Check |
|---|---|
| Login page says database unavailable | MySQL service, host/port, password, `DB_NAME=sems_db` |
| Access denied | `sems_app` password and grants; avoid using root permanently |
| Unknown database | Execute `00_database_setup.sql` |
| Missing table/view | Stop and rerun from the first failed numbered script after a guarded reset |
| Invalid demo credentials | Generate bcrypt hash and map exact seeded email |
| MySQL tests skipped | Set `SEMS_TEST_DATABASE_URL` to a database ending `_test` |
| Duplicate nullable location allowed by SQL | UI/service null-normalized check must be used; see known issues |
| Preflight reports package imports missing | Activate `.venv`, then run `pip install -r requirements.txt` |
| Browser says API unavailable | Start Uvicorn on port 8000; check only `NEXT_PUBLIC_SEMS_API_URL` in `frontend/.env.local` |
| `npm run build` fails | Run `npm ci`, then type-check/lint first; do not bypass errors with a development-only build |
| npm audit cannot reach the registry | Restore normal approved internet access and rerun the complete acceptance; do not mark package audit passed from an old result |
| API returns 401 after restart | Process-local sessions intentionally expire on restart; sign in again |
| CORS/trusted-host denial | Keep frontend/API on configured local hosts or update explicit allowed values in `.env` |
| Session stops after a role/lab/status edit | Sign in again; database identity intentionally invalidates stale sessions |

## 13. Optional backup

Before a reset, use Workbench **Server → Data Export** for only `sems_db`, including routines/triggers, or follow the optional `mysqldump` commands in `MYSQL_WORKBENCH_EXECUTION_GUIDE.md`. Confirm the backup file exists before dropping anything.
