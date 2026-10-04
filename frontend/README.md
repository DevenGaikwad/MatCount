# SEMS Professional Frontend

This directory is the canonical presentation source for SEMS. It uses Next.js, React, strict TypeScript and Tailwind CSS, and communicates only with the thin Python API. It never connects to MySQL or contains database credentials/business transactions.

## Local development

From the project root, start the Python API in terminal 1:

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

In terminal 2:

```powershell
Set-Location frontend
npm ci
npm run dev
```

Open `http://127.0.0.1:3000`.

`NEXT_PUBLIC_SEMS_API_URL` is the only approved browser-visible environment value. Copy `.env.local.example` only when the API address differs from the default; never add DB values or authentication hashes.

## Quality commands

```powershell
npm run typecheck
npm run lint
npm run test
npm run build
```

The project-wide Windows gate is preferred for final regression:

```powershell
.\scripts\final_acceptance.ps1
```

## Structure

- `app/`: login, authenticated shell and routes.
- `features/`: module-specific views/workflows.
- `components/`: shell, feedback and reusable design-system controls.
- `lib/`: auth, API client, permissions, formatting and data loading.
- `types/`: transport contracts.

Role-aware navigation is a usability control only. FastAPI dependencies and Python services independently enforce current account, role and laboratory scope.
