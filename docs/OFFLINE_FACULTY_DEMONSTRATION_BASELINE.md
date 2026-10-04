# Offline faculty demonstration baseline

Verified on 4 October 2026 by SHA-256 comparison of file bytes. Different archive roots alone were normalized; file contents and line endings were not normalized.

## Immutable provenance and candidate

| Artifact | SHA-256 | Status |
|---|---|---|
| `SEMS_Final_Academic_Professional_Release_v2.zip` | `bf7c69e72a03ee50296ea1cdaa45764317b93676712866c38885fb47ebff60b0` | Private faculty feature/provenance baseline; original vulnerable dependency lock retained unchanged |
| `MatCount_SEMS_v2_Academic_Release_Candidate_RC1.zip` | `297890379300798ff0a57d7310c458ca45c761b36959423f8450cdb63b12ecf8` | First security-hardened publication derivative |

RC1 source maps to commit `147d285eaa8ab4beed274da3b2adedf45648c36b`. The intended immutable tag is `v2.0.0-rc.1`; tag/release creation is separate from this source comparison. All 253 RC1 archive entries equal their GitHub counterparts byte for byte. GitHub contains one additional external checksum file, `release/MatCount_SEMS_v2_Academic_Release_Candidate_RC1.zip.sha256`; an archive cannot contain a checksum of itself.

## Faculty-visible parity

Exactly 13 production relations, seven production views and two production triggers remain unchanged. Application/API routes, services, repositories, database model/settings source, frontend feature/component/UI source, Streamlit pages, tests, schema/views/routines/triggers/seed SQL and academic demonstrations are byte-identical. The ETCS302 collection contains 13 SQL scripts plus an isolated optional NoSQL teaching extension. There are zero unexplained differences and zero faculty-visible functional differences.

The original ZIP contains 227 files; RC1 contains 253. There are 33 added/changed paths in the following complete classification.

### Dependency/security patch

| Change | Path |
|---|---|
| changed | `frontend/package-lock.json` |
| changed | `frontend/package.json` |

### Build/acceptance tooling

| Change | Path |
|---|---|
| added | `scripts/check_docs_links.py` |
| added | `scripts/check_npm_audit.py` |
| changed | `scripts/final_acceptance.ps1` |
| added | `scripts/verify_release_artifacts.py` |

### GitHub governance/CI

| Change | Path |
|---|---|
| added | `.editorconfig` |
| added | `.gitattributes` |
| added | `.github/ISSUE_TEMPLATE/acceptance.md` |
| added | `.github/ISSUE_TEMPLATE/bug_report.md` |
| added | `.github/ISSUE_TEMPLATE/config.yml` |
| added | `.github/ISSUE_TEMPLATE/documentation.md` |
| added | `.github/dependabot.yml` |
| added | `.github/pull_request_template.md` |
| changed | `.github/workflows/ci.yml` |
| added | `.github/workflows/release-integrity.yml` |
| added | `.github/workflows/security.yml` |
| changed | `.gitignore` |
| added | `AUTHORS.md` |
| added | `CITATION.cff` |
| added | `CODE_OF_CONDUCT.md` |
| added | `CONTRIBUTING.md` |
| added | `CONTRIBUTORS.md` |
| added | `SECURITY.md` |

### Release/documentation metadata

| Change | Path |
|---|---|
| added | `CHANGELOG.md` |
| changed | `README.md` |
| added | `docs/GITHUB_PUBLICATION_RUNBOOK.md` |
| changed | `docs/LOCAL_ACCEPTANCE_CHECKLIST.md` |
| added | `docs/PUBLICATION_READINESS_2026-10-04.md` |
| added | `docs/SECURITY_REMEDIATION_2026-10-04.md` |
| added | `docs/screenshots/README.md` |
| added | `release/README.md` |
| added | `release/SEMS_Final_Academic_Professional_Release_v2.zip.sha256` |

## Reviewed security and build changes

- Next.js changes from the original range resolving 16.3.2 to exact 16.3.6; sharp changes from 0.35.3 to 0.35.5 in the regenerated lock.
- The production command changes from `next build` to the supported `next build --webpack` path.
- `scripts/final_acceptance.ps1` invokes `scripts/check_npm_audit.py`; the gate requires zero runtime findings and allows only the exact documented development-only braces advisory chain.
- Governance, CI, author/citation/reuse policies, README/status wording, acceptance and screenshot intake documentation, link checks and release-integrity tooling describe publication and remaining acceptance.

## Demonstration boundary

Prefer the patched, hash-verified RC1 to the original uploaded ZIP for a faculty run. Use synthetic data, private ignored local configuration, local MySQL and localhost API/frontend services. Initial tool/dependency installation can require internet; locally executable does not mean fully air-gapped. Never show passwords, tokens, credential hashes or unrelated private information in screenshots.

Fresh Windows PowerShell, MySQL 8.4.11, disposable `_test` integration, MySQL Workbench/CLI proof, four-role workflows and genuine desktop/mobile/accessibility acceptance remain pending. Source parity is not execution or faculty approval.

Later reviewed dependencies or setup-tool corrections can advance `main`. Faculty evidence must identify an immutable candidate/tag and matching hash-verified package. A changed package must use a new candidate identifier and filename; neither original archive nor RC1 may be overwritten or retagged. A newer candidate must preserve this same functional comparison and disclose every added dependency/tooling change.
