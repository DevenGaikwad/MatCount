# MatCount RC1 security remediation and validation

**Date:** 2026-10-04  
**Scope:** Patch the original v2 frontend dependency graph for academic GitHub publication without changing the frozen database schema or application business logic. This report does not claim fresh Windows/MySQL acceptance.

## Original finding and correction

The immutable original v2 ZIP resolves `next@16.3.2` and `sharp@0.35.3`, with critical/high runtime audit findings recorded in [the initial audit](PUBLICATION_READINESS_2026-10-04.md). It remains unchanged under SHA-256 `bf7c69e72a03ee50296ea1cdaa45764317b93676712866c38885fb47ebff60b0`.

The reviewed candidate pins `next@16.3.6`; a regenerated npm lock resolves `sharp@0.35.5`. This addresses the maintainer-reported fixed ranges for [Windows-hosted Next.js RCE](https://github.com/vercel/next.js/security/advisories/GHSA-p293-qw3h-jr36), [AVIF image optimization](https://github.com/vercel/next.js/security/advisories/GHSA-2xp9-vwfh-vxw4), [ImageResponse](https://github.com/vercel/next.js/security/advisories/GHSA-vcvr-r3jv-pc5j) and [sharp/libheif](https://github.com/lovell/sharp/security/advisories/GHSA-rgj7-g3m4-5g8c). The fresh **runtime-only `npm audit --omit=dev` returns zero findings**. This is a dependency audit result, not a blanket security guarantee.

Compatible lockfile-only npm fixes reduced the full audit to **five high affected development packages** (`braces`, `micromatch`, `fast-glob`, `@next/eslint-plugin-next`, `eslint-config-next`). They all derive from [GHSA-vfj7-8cjw-p6xm](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm), for which the advisory lists **no patched release** as of this review. The affected chain is used by ESLint tooling, not the installed runtime dependency graph. `scripts/check_npm_audit.py` fails on any runtime finding, unexpected package/severity or additional advisory and prints the exact exception; the CI security workflow and Windows acceptance script invoke it. Do not run an unrelated breaking downgrade such as `npm audit fix --force` to make the report visually empty. Revisit the exception when an upstream fix is published.

Next.js 16 normally builds with Turbopack. In this execution environment its CSS worker cannot bind a local port, even with broader sandbox permission, so the candidate uses the officially supported `next build --webpack` production build. That command completed successfully for 14 generated pages. No browser behavior or UI workflow is inferred from a build alone.

## Fresh source checks

| Check | Result | Boundary |
|---|---|---|
| SQL static contract | PASS: exactly 13 production relations and seven views; 13 ETCS302 SQL scripts plus optional NoSQL | No live server here |
| Server-independent Python/API | **131 passed**, 20 MySQL integration cases deselected | Python 3.12 virtual environment |
| Dedicated API | **17 passed** | TestClient; no live MySQL |
| Focused RBAC/financial protection | **30 passed** | Tests, not live four-role demonstration |
| `pip check` and secret scan | PASS | Config templates only |
| Frontend TypeScript and ESLint | PASS, zero lint warnings | Updated lock |
| Frontend Vitest | **10 passed** | Updated lock |
| Frontend production build | PASS, 14 generated pages | Official Webpack build path |
| npm runtime audit | PASS, zero findings | Registry snapshot on review date |
| npm full audit | Five known dev-only high affected packages; exact exception gate PASS | Unfixed `braces` advisory remains visible |
| Original v2 ZIP | Integrity/SHA-256 PASS, unmodified | Historical provenance, not patched release |

Fresh Windows PowerShell, MySQL 8.4.11/`sems_test`, MySQL Workbench SQL execution, role-workflow, human browser/accessibility review and genuine screenshots are **pending**. The project remains a **release candidate** until those gates are complete.

## Package and GitHub boundary

The corrected candidate ZIP is a *new* immutable artifact with a distinct checksum and matching GitHub prerelease assets. The original v2 archive must remain private rollback/provenance and is not a patched release asset. Aaryan Sachin Anand (PRN 1022411049) precedes Deven Sachin Gaikwad (PRN 1022411052) in formal records. Aaryan's collaborator invitation waits for his exact username; no GitHub contributor statistics are manufactured.
