# MatCount changelog

This repository-level summary records the publication candidate; the implementation history is in [docs/CHANGELOG.md](docs/CHANGELOG.md). Dates, release tags and final acceptance will be added only after the corresponding events occur.

## Unreleased — SEMS v2 academic release candidate

### Included

- Premium Next.js/React/TypeScript presentation and thin FastAPI boundary over the existing Python services and repositories; Streamlit preserved as a fallback.
- Backend/API and CSV financial-data minimization, role/lab access controls and keyboard/dialog accessibility refinements.
- Workbench-ready setup, schema, seed, verification and faculty demonstration material, with 13 ETCS302 SQL scripts and an optional isolated NoSQL extension.
- Static schema and academic contract checks, server-independent tests, frontend checks, secret hygiene and Windows final-acceptance tooling.
- MatCount repository identity, academic attribution and governance documentation.

### Preserved

- Frozen 13-relation production schema and seven production views; no production schema expansion.
- The original v2 archive's SHA-256 and the pre-modernization rollback boundary.

### Still required

- Fresh Windows/MySQL 8.4.11 and Workbench execution, safe `sems_test` integration, four-role workflows, genuine visual/accessibility evidence and explicit final academic acceptance.
- Fresh review of the development-only `braces` advisory when an upstream fix becomes available. The runtime findings were remediated in the patched candidate; see [the security review](docs/SECURITY_REMEDIATION_2026-10-04.md).

### 2026-10-04 security-patch candidate

- Pinned Next.js 16.3.6; the regenerated lock resolves sharp 0.35.5 and retains no runtime npm findings.
- Applied compatible lockfile-only npm fixes; five high affected development packages remain in one unfixed `braces` chain. The exact advisory is allowlisted by a failing-on-change CI audit policy, not suppressed from output.
- Re-ran 131 server-independent Python cases, 17 API cases, 30 focused RBAC/financial cases, 10 frontend tests, TypeScript, zero-warning ESLint, and the 14-page official Webpack production build.
- Updated the Windows acceptance audit policy and created a separate release-candidate integrity process. Original v2 bytes and SHA-256 remain unchanged.

No GitHub prerelease, published tag or completed local acceptance is implied by this entry.
