# Dependency security remediation on 26 October 2026

## Scope and baseline

This maintenance change addresses [security issue #41](https://github.com/DevenGaikwad/MatCount/issues/41). The owner completed the academic demonstration and subsequently requested actual remediation of the dependency alerts before any repository archival.

The live Dependabot inventory contained **93 open alerts**, rather than 93 separate affected packages. The [complete numbered inventory](security/DEPENDABOT_2026-10-26.json) records their titles and identifiers.

| Affected package | Baseline alerts | Remediation in reviewed source |
|---|---:|---|
| Pillow | 82 across the Linux and Windows locks, representing 41 advisories | 12.3.0 → 13.0.0 in both hash-verified locks |
| certifi | 2, one per platform lock | 2026.7.22 → 2026.10.19 in both locks |
| Next.js | 3 | next and eslint-config-next 16.3.8 → 16.4.3 together |
| Vite and bundled launch-editor | 6 | Transitive Vite 8.3.2 → 8.3.5 |
| Zod | Additional finding in the fresh npm audit | Transitive Zod 4.4.3 → 4.6.7 |

Streamlit 1.65.0 requires Pillow <13. Updating Pillow alone would produce an incompatible environment, so Streamlit is updated to 1.66.1, whose metadata permits Pillow <14. Pillow and certifi are now explicit exact direct pins as well as hashed platform pins. Other Python package versions are retained. The npm resolver also refreshes the relevant Next native packages, Vite/Rolldown bindings, PostCSS and nanoid within their permitted dependency ranges.

## Observed local verification

Environment: Linux x86_64, Python 3.12.14, Node.js 24.22.1, npm 11.9.0 and official MySQL Community Server 8.4.11. GitHub CI retains its configured Node 24.19.0 runtime. Local results do not stand in for native Windows execution; the PR's existing Windows candidate workflow must pass before merge.

| Check | Observed result |
|---|---|
| Linux hash-verified dependency installation and pip check | PASS, no broken requirements |
| pip-audit of Linux lock | 59 packages, zero known vulnerabilities |
| pip-audit of Windows lock | 59 packages, zero known vulnerabilities |
| Windows CPython 3.12 wheel download and SHA-256 checks | All 59 pinned wheels verified; this checks wheel availability/hashes, not Windows runtime behavior |
| SQL build into disposable sems_security_test | PASS, MySQL 8.4.11; production database not used |
| Full pytest with live MySQL integration | 151 passed; existing Starlette/httpx deprecation warning remains |
| Frontend typecheck, lint and runtime/negative lint probes | PASS |
| Frontend Vitest | 10 passed |
| Production frontend build | PASS, 14 generated routes |
| npm audit, complete graph | Zero findings, including development dependencies |
| npm audit --omit=dev | Zero findings |
| Existing npm audit policy script | PASS, zero runtime and full findings |
| Streamlit login rendering | PASS, no AppTest exceptions, Email and Password fields present |
| Pillow PNG, JPEG, TIFF and GIF round trips | PASS |
| API health and production login HTTP smoke check | HTTP 200 for both entry points; this smoke check alone does not establish database acceptance |

The dependency audit policy is not disabled or widened. No vulnerability is dismissed as a false positive, and no security setting is turned off. GitHub marks dependency alerts fixed only after it analyses the updated default branch. Review the PR checks and the live Dependabot page for the post-merge status; a branch-local audit is not itself proof that GitHub has completed that analysis.

## Boundaries and future installation

The application source, role/lab rules, 13 production relations, seven production views, routines, triggers and tests are unchanged by this maintenance. Existing ESLint peer-range warnings remain visible; the established compatibility adapter and its negative probes pass. The published v2.0.0-rc.2 tag and asset bytes are retained for provenance and still contain their original dependency snapshot. The repaired source is not a replacement of that historical ZIP.

For a future installation, use the reviewed main source and its current locks. On an existing Windows installation, back up the project/private configuration, obtain the corrected source, then run from its root:

```powershell
.\.venv\Scripts\python.exe -m pip install --require-hashes -r requirements-windows.lock.txt
Push-Location frontend
npm ci
Pop-Location
.\.venv\Scripts\python.exe scripts\check_npm_audit.py
```

Retain private configuration and database data. Dependency maintenance does not require schema recreation or reseeding. Run the documented acceptance checks in a dedicated *_test database before relying on the refreshed installation. No change to the user's existing laptop installation is performed by this GitHub maintenance.

## Primary sources

- [Pillow multi-frame storage advisory and fixed version](https://github.com/python-pillow/Pillow/security/advisories/GHSA-v9pv-5gc8-w2m6)
- [Pillow 13.0.0 release](https://github.com/python-pillow/Pillow/releases/tag/13.0.0)
- [certifi advisory and corrected version range](https://github.com/advisories/GHSA-6q48-6c7w-9gw2)
- [Streamlit 1.66.1 published dependency metadata](https://pypi.org/pypi/streamlit/1.66.1/json)
- [Next.js upstream security update](https://nextjs.org/blog/nextjs-security-update-october-14-2026)
- [Vite 8.3.5 release](https://github.com/vitejs/vite/releases/tag/v8.3.5)
- [Zod oversized collection advisory](https://github.com/advisories/GHSA-mrhx-c7xc-m3w5)
