# MatCount publication readiness — security hold

**Historical finding:** The runtime advisories identified below were corrected in a separately checksummed candidate later on 2026-10-04. See [the current security remediation record](SECURITY_REMEDIATION_2026-10-04.md). This document preserves the original v2 audit evidence.

**Review date:** 2026-10-04  
**Decision:** Local repository preparation may continue; do not create a public repository, merge/publicize the vulnerable package, or publish the original v2 ZIP as a prerelease asset. No final academic acceptance is claimed.

## Authoritative source and static evidence

The recovered original `SEMS_Final_Academic_Professional_Release_v2.zip` is readable (275 entries) and its SHA-256 and supplied checksum agree: `bf7c69e72a03ee50296ea1cdaa45764317b93676712866c38885fb47ebff60b0`. It was extracted into a fresh staging tree. The source-only SQL validator confirms **13 production relations, seven production views and 13 ETCS302 SQL demonstrations**, with the optional NoSQL extension isolated. The project secret scanner, release verifier, Python compile of added scripts and local Markdown file-link checker passed. A clean extraction of the prepared handoff bundle repeated the static contract, secret, digest and file-link checks successfully. No live MySQL, Windows acceptance or new full application regression was performed in this staging environment.

## Fresh npm audit finding

The original package lock resolves **Next.js 16.3.2** (`frontend/package.json` allows `^16.3.0`) and transitive **sharp 0.35.3**. On 2026-10-04, `npm audit --omit=dev --audit-level=high --json` exited 1: **one critical package (`next`) and one high package (`sharp`)**, counting affected packages rather than distinct advisories. The unfiltered audit exited 1 with **one critical and 23 high affected packages**, many through development-only ESLint chains. This is a fresh finding that supersedes the August report's “npm audit pending” statement; the original v2 ZIP was not modified.

| Locked dependency | Path / impact | Advisory | Patched range reported by maintainers |
|---|---|---|---|
| `next@16.3.2` | Direct runtime dependency; Windows server RCE | [GHSA-p293-qw3h-jr36](https://github.com/vercel/next.js/security/advisories/GHSA-p293-qw3h-jr36) | 16.3.3+ |
| `next@16.3.2` | Direct runtime dependency; AVIF image optimization | [GHSA-2xp9-vwfh-vxw4](https://github.com/vercel/next.js/security/advisories/GHSA-2xp9-vwfh-vxw4) | 16.3.3+ |
| `next@16.3.2` | Direct runtime dependency; `next/og` ImageResponse advisory (use-path exposure requires review) | [GHSA-vcvr-r3jv-pc5j](https://github.com/vercel/next.js/security/advisories/GHSA-vcvr-r3jv-pc5j) | 16.3.6+ |
| `sharp@0.35.3` | Transitive runtime dependency through Next.js; libheif | [GHSA-rgj7-g3m4-5g8c](https://github.com/lovell/sharp/security/advisories/GHSA-rgj7-g3m4-5g8c) | 0.35.4+ |

No `next/og` import was found in the project's frontend source, but this does not dismiss the Windows-hosted or image-optimization findings, nor does it convert an audit failure into a pass. The npm output reported `fixAvailable: false` for the current dependency graph; this is not proof that patched releases do not exist. A separately reviewed patch to the lockfile/manifest and full compatibility assessment are required. Do not run `npm audit fix --force`, silently repackage the original ZIP, or attach its old digest to changed bytes.

## Publication and identity gates

- GitHub authenticated login was verified as `DevenGaikwad`; `DevenGaikwad/MatCount` returned not found at the time of review. The available connector does not expose repository creation, collaborator invitation, release upload, branch rules or milestone administration; browser fallback requires explicit user approval. **No repository, branch, commit, PR, tag, issue, invitation or release has been created.**
- Aaryan Sachin Anand's exact GitHub username is unconfirmed. Team credits list Aaryan (PRN 1022411049) before Deven (PRN 1022411052), but do not imply a collaborator invitation or genuine GitHub commit attribution.
- No open-source licence was selected. Repository documentation includes an academic-review/no-licence notice; explicit reuse rights remain with the authors. An initial private repository could be considered only after permission and source-security decision, with public transition gated by corrected dependency and full checks.
- Windows PowerShell, MySQL 8.4.11/`sems_test`, Workbench execution, current role workflows, screenshot/privacy review and genuinely observed visual/accessibility acceptance remain pending.

## Safe remediation path

1. Review patch versions, dependency tree and exposure; update Next.js/sharp through a compatible, reviewed dependency change without weakening tests, then rerun both full and runtime npm audits.
2. Re-run TypeScript, ESLint, Vitest, production build, Python/API/RBAC suites, frozen SQL contract and secret checks; perform fresh Windows/MySQL/Workbench acceptance against `sems_test` and `sems_db` as instructed.
3. Package a new corrected release candidate with a *new* name/checksum, verify it from a clean extraction and preserve the original v2 as private provenance. Review third-party rights and screenshot metadata before any public transition.
4. Obtain explicit browser-fallback approval (or a capable approved GitHub interface) and Aaryan's exact username, then create an initially private repo, run CI, configure governance, invite the verified user and publish only a reviewed safe prerelease.

Until these gates are met, GitHub publication and the original-v2 prerelease are **blocked**, not partially complete.
