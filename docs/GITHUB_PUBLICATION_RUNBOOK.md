# MatCount GitHub publication runbook — gated, not executed

This is a workflow checklist, not proof that each GitHub setting has been completed. The [original security finding](PUBLICATION_READINESS_2026-10-04.md) was addressed for runtime dependencies in the [patched candidate](SECURITY_REMEDIATION_2026-10-04.md). Do not publish the original vulnerable v2 ZIP. The original digest remains provenance, never the checksum of patched bytes.

## Repository identity

| Setting | Intended value / gate |
|---|---|
| Owner and name | Authenticated `DevenGaikwad/MatCount`; recheck nonexistence/identity before creation |
| Visibility | Private first; public only after rights, secrets, runtime audit and CI gates pass with explicit publication intent |
| Description | Academic MySQL 8.4, FastAPI and Next.js system for electronic-component inventory, laboratory requests, transfers, RBAC workflows and faculty SQL demonstrations. |
| Default branch | `main` |
| Topics | `mysql`, `mysql-workbench`, `fastapi`, `nextjs`, `typescript`, `sqlalchemy`, `pymysql`, `rbac`, `inventory-management`, `electronics-lab`, `academic-project`, `etcs302`, `database-management` |
| Homepage | None unless a real deployment is verified |
| Licence | None granted; keep the academic-review notice in README |

## Import and review sequence

1. Verify the newly patched package digest, source rights, archive safety and exclusions. The user authorized publication and authenticated browser fallback on 2026-10-04; Aaryan's exact GitHub username will be supplied later, so proceed without claiming or sending his invitation now.
2. Confirm the Git author identity belongs to the person genuinely committing; do not use a generic service identity or impersonate either student. Inspect any existing repository, remote, tags, branch and history before initializing or importing. Do not overwrite an unrelated repository.
3. Create a private repository under the verified owner, a minimal genuine seed commit on `main` if suitable, then an import branch `release/academic-v2-candidate`. Import audited source and MatCount governance files; do not commit the release ZIP, `.env`, private rollback, `node_modules`, `.next`, virtual environments, dumps, caches or local screenshots. The checksum committed to `release/` must correspond to the *actual new* candidate asset.
4. Open a publication PR recording checksum, frozen 13/7 contract, ETCS302 count, source exclusions, audit outcome and pending Windows/MySQL/Workbench evidence. Run actual CI; correct failures narrowly. Merge only after required checks pass. No force push or fictional co-author attribution.
5. Invite the exact verified Aaryan account with write access; verify invitation status separately from acceptance. Deven is the personal-account owner and needs no redundant invitation. Add `CODEOWNERS` only after both usernames and review responsibilities are verified.
6. Create labels, milestone and open acceptance issues below. Configure `main` ruleset against *observed* job names: deny force push/deletion, require passing CI/resolved conversations; require one review only when actual reviewer access cannot deadlock the team. Enable private vulnerability reporting, Dependabot alerts/security updates, secret scanning and push protection where available. Do not assume private personal-repository CodeQL/dependency-review entitlement; confirm feature availability before adding a required workflow.
7. Create a **prerelease**, not a final release, only from the reviewed merge commit with a nonconflicting RC tag. Attach the newly verified package/checksum, redownload the asset and compare its SHA-256. Verify tag target and prerelease flag. Never reuse `v2.0.0-rc.1` if it already exists.
8. Clone into a new clean directory and inspect rendered README, links, team order, CI, excluded files, checksum, archive content, package installation, tests and build. This still does not substitute for the intended Windows/MySQL 8.4.11 acceptance.

## Milestone: v2 Final Academic Acceptance

Create the following **open** issues with labels suited to the actual repository. Attach sanitized evidence and close only after review:

| Issue | Acceptance evidence | Suggested labels |
|---|---|---|
| Run final Windows and MySQL 8.4.11 acceptance | Verified package digest, separate `sems_db`/`sems_test`, actual `.\scripts\final_acceptance.ps1` result with integration tests executed | `acceptance-required`, `mysql`, `backend` |
| Capture MySQL Workbench proof | Version/database, 13 tables, seven views, keys, verification query, JOIN, view and application-write SELECT | `acceptance-required`, `workbench`, `faculty-demo` |
| Review unfixed development-tool advisory | Runtime zero findings, exact `braces` exception, upstream patch watch and re-audit | `acceptance-required`, `security`, `frontend` |
| Complete all role workflows | Student, Faculty, Lab Assistant, Administrator, API/CSV privacy and transaction-state evidence | `acceptance-required`, `backend`, `security` |
| Complete genuine UI/accessibility acceptance | Desktop/mobile, modal focus trap/restore, visible focus, screenshots without secrets | `acceptance-required`, `frontend`, `faculty-demo` |
| Promote candidate to final academic release | Previous issues closed with evidence, acceptance report updated, fresh checksum/tag/release notes | `release-candidate`, `documentation` |

Do not mistake GitHub's generated Contributors graph for the formal [academic team record](../CONTRIBUTORS.md). Contributor attribution requires real commits. Final release is a separate decision after the entire milestone is accepted.
