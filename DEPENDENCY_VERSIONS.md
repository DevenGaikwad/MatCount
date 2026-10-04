# RC2 dependency versions

The archive records its exact source in `SOURCE_COMMIT.txt`. Python direct requirements are exact pins. Windows x64/CPython 3.12 and Linux x86_64/CPython 3.12 have complete wheel hashes in their respective lockfiles. Frontend direct pins and the complete npm lock freeze the validated graph.

## Runtimes

- Intended host: Windows 10/11 x64; MySQL Server 8.4.11 LTS and MySQL Workbench as an independent client.
- Python: 3.12 (validation interpreter 3.12.14; record the actual CI/host patch version in the external report).
- Node: 24.19.0 LTS; npm: 11.9.0. Frontend engine: `>=24.19.0 <25`.

## Python direct dependencies

| Package | Pinned version |
|---|---|
| streamlit | 1.65.0 |
| SQLAlchemy | 2.0.54 |
| PyMySQL | 1.2.3 |
| pandas | 2.3.3 |
| plotly | 6.9.0 |
| python-dotenv | 1.2.4 |
| bcrypt | 4.3.0 |
| pytest | 9.0.3 |
| fastapi | 0.141.1 |
| uvicorn[standard] | 0.54.0 |
| httpx | 0.28.1 |

## Frontend direct dependencies

| Package | Pinned version |
|---|---|
| next | 16.3.8 |
| react | 19.3.0 |
| react-dom | 19.3.0 |
| @eslint/compat | 2.1.1 |
| @tailwindcss/postcss | 4.3.3 |
| @types/node | 24.13.3 |
| @types/react | 19.3.0 |
| @types/react-dom | 19.3.0 |
| eslint | 10.11.0 |
| eslint-config-next | 16.3.8 |
| tailwindcss | 4.3.3 |
| typescript | 6.0.3 |
| vitest | 5.0.3 |
| sharp (transitive runtime) | 0.35.5 |

## Selection and remaining boundaries

Next.js 16.3.8 is the stable security patch selected after official release/advisory review; sharp remains the stable 0.35.5. React and React DOM are both 19.3.0. Vitest 5.0.3 and TypeScript 6.0.3 passed the configured checks. The TS 7 update is excluded because typescript-eslint rejects it.

ESLint 10.11.0 runs the existing Next/React/accessibility rules through the officially maintained `@eslint/compat` 2.1.1 adapter. All 113 existing configured rules retain their severity, and negative probes detect react/display-name, jsx-a11y/alt-text and @next/next/no-img-element. Native peer-range warnings from legacy React/import/accessibility plugins remain visible; this is adapter-based compatibility, not a claim of native plugin ESLint 10 support. No lint rule or gate was disabled.

SQLAlchemy remains on supported 2.0 maintenance (2.0.54); the 2.1 migration is deferred pending live MySQL acceptance. PyMySQL is frozen at 1.2.3 to retain the upstream 1.2.1 security fix, which must not be discarded by downgrading. pandas remains 2.3.3 until report/CSV/fallback migration acceptance for pandas 3.

The npm audit policy remains unchanged: zero runtime findings; only the exact development-only GHSA-vfj7-8cjw-p6xm chain can be excepted. The intended host must repeat audits. Locks make installation reproducible within the stated architecture/runtime targets; they do not make the bundle fully air-gapped or prove live MySQL/Windows/role acceptance.

The new post-interruption PR #22 consistently updated the direct pytest pin and both hashed locks to 9.0.3. Its official stable release fixes CVE-2025-71176 and supports Python 3.12. The existing Linux and Windows gates passed on its exact head; the final package repeats its extracted-source gates. No application, schema or test assertion changed in this update.
