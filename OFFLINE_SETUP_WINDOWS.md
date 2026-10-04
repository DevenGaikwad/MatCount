# Windows local setup and acceptance

Start with [FACULTY_DEMO_START_HERE.md](FACULTY_DEMO_START_HERE.md). Supported bundle target: **Windows x64, CPython 3.12, Node 24.19.0 with npm 11.9.0, MySQL Server 8.4.11**. The Windows lock selects Windows wheels; use `requirements-linux.lock.txt` only for the documented Linux validation environment. Neither installed dependencies nor a MySQL installation/data directory is bundled.

## Workspace and dependency installation

Open the newly extracted versioned folder in VS Code. Paths containing spaces are supported. Open a PowerShell terminal at that root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -m pip install --require-hashes -r requirements-windows.lock.txt
.\.venv\Scripts\python.exe -m pip check
npm install --global npm@11.9.0
npm --version
Push-Location frontend
npm ci
Pop-Location
```

Direct Python manifests are pinned; the full Windows dependency lock also pins and hashes every selected wheel. `npm ci` installs the exact frontend lock. Do not use `latest`, `npm audit fix --force`, or installed folders from another machine. Installation initially requires internet unless the matching tools and package caches are already available.

Copy configuration examples without overwriting an existing private configuration:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
if (-not (Test-Path frontend/.env.local)) { Copy-Item frontend/.env.local.example frontend/.env.local }
```

Privately fill database settings and generated login hashes. Configure `sems_app` with only the required privileges on `sems_db` using an authorized local MySQL administrator. MySQL Workbench is a client; MySQL Server must be running independently. Only Python connects to MySQL. Browser configuration contains the non-sensitive API address only.

For a fresh database, execute scripts `00` through `07` in the exact order in [the Workbench guide](docs/MYSQL_WORKBENCH_EXECUTION_GUIDE.md). Do not automatically drop/reset/reseed a database that contains existing work. `sql/99_reset_database.sql` is not part of normal setup or the acceptance orchestrator.

## Disposable integration database

Create a fresh disposable `sems_test` with the guarded builder. It is exclusively for tests; tests can change/delete its rows. The application database remains `sems_db`.

```powershell
.\.venv\Scripts\python.exe scripts/build_database.py --database sems_test --user root
```

The builder prompts for the local MySQL administrative password. Then set the integration URL in this terminal without typing a password into a public command or printing the URL:

```powershell
$testCredential = Get-Credential -UserName root -Message 'Local disposable sems_test account'
$encodedTestPassword = [Uri]::EscapeDataString($testCredential.GetNetworkCredential().Password)
$env:SEMS_TEST_DATABASE_URL = "mysql+pymysql://root:${encodedTestPassword}@127.0.0.1:3306/sems_test?charset=utf8mb4"
.\.venv\Scripts\python.exe scripts/test_database_safety.py
.\scripts\final_acceptance.ps1
Remove-Item Env:SEMS_TEST_DATABASE_URL -ErrorAction SilentlyContinue
Remove-Variable encodedTestPassword, testCredential -ErrorAction SilentlyContinue
```

Do not print or screenshot private configuration, credential prompts, tokens or hashes. If an existing `DB_PASSWORD` process variable belongs to a different account, use a new terminal for the builder so its secure prompt obtains the intended test administrator's credential. The test guard rejects `sems_db` and any database name that does not end in `_test`.

If PowerShell blocks the script, and you trust the verified local archive, allow scripts for this terminal only with `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then run the acceptance command again. A missing/unsafe test target must produce a failed acceptance result, not a silently green final result. Only the full command establishes the automated scope; `-Fast`, `-FrontendOnly` and `-BackendOnly` remain explicitly partial modes.

## Local services

Terminal 1, at the project root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Terminal 2:

```powershell
Set-Location frontend
npm run dev -- --hostname 127.0.0.1 --port 3000
```

For a built frontend, run `npm run build` first, then `npm run start -- --hostname 127.0.0.1 --port 3000`. The committed build uses Webpack. API: `http://127.0.0.1:8000/api/health`. Frontend: `http://127.0.0.1:3000`. A healthy HTTP API response can still report an unavailable database; check the response's database status.

Optional fallback, in another project-root terminal:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

Stop services with Ctrl+C in each owning terminal and wait for clean exit. These commands do not stop MySQL or delete data. Complete genuine Workbench, Administrator/Faculty/Lab Assistant/Student, desktop/mobile, keyboard/focus and faculty acceptance before promoting this candidate to a final academic release.
