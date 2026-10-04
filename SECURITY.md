# Security policy

## Scope and support

The SEMS v2 source is a release candidate for academic demonstration, not a production-hosted service and not yet a final accepted academic release. Security fixes should preserve the frozen 13-relation/seven-view database contract and be tested against a separate `_test` database.

## Private reporting

If GitHub private vulnerability reporting is enabled for this repository, use the repository's **Security → Report a vulnerability** flow. If it is not enabled, contact the repository maintainers privately through a verified channel; no security mailbox has been designated in this project. Do **not** disclose exploit details, tokens, credentials, hashes, private configuration, real student information or financial records in a public issue or pull request.

Include a minimal reproducible case using fictional data, affected component/version, expected versus observed behavior and whether a runtime or development dependency is involved. Do not test against someone else's live installation. Maintainers should triage privately, review backend/API and CSV data exposure, patch with regression tests and publish a sanitized advisory when appropriate.

The frontend must never receive MySQL credentials, reusable password hashes or unauthorized student/faculty financial fields. Local demonstration secrets belong only in ignored configuration. Dependency alerts require assessment of exact path, exploitability and upgrade compatibility; avoid unreviewed `npm audit fix --force` or breaking major upgrades.
