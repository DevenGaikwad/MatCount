# RC2 source and dependency freeze review — 2026-10-04

This is an academic release candidate. Actual Windows laptop/MySQL 8.4.11/Workbench/four-role/visual/faculty acceptance remains pending in issues #2–#7. See [the immutable faculty baseline comparison](OFFLINE_FACULTY_DEMONSTRATION_BASELINE.md).

## Selected changes

- Next.js 16.3.8 includes the latest reviewed stable security fixes. The corresponding eslint-config-next is pinned to the same version; sharp remains 0.35.5. [Official Next.js release](https://github.com/vercel/next.js/releases/tag/v16.3.8).
- React and React DOM are pinned together at 19.3.0. PR #17's lock updated both; Dependabot therefore closed redundant PR #16. A tooling gate now rejects mixed runtime versions. [Official React release](https://github.com/react/react/releases/tag/v19.3.0).
- Vitest 5.0.3 requires supported modern Node/Vite versions; the selected Node 24.19.0 meets its migration prerequisites. [Official migration guide](https://vitest.dev/guide/migration.html).
- TypeScript 6.0.3 is within the parser's supported `<6.1.0` range. The TS 7 PR failed the actual lint/parser check and was closed; this freeze does not suppress that check. [Official TypeScript 6 announcement](https://devblogs.microsoft.com/typescript/announcing-typescript-6-0/).
- ESLint 9 reached its documented end of support. ESLint 10.11.0 uses maintained @eslint/compat 2.1.1 to adapt the existing legacy plugin rule APIs. All 113 existing rule severities are retained. Negative probes require React display-name, accessibility alt-text and Next image rules to detect actual violations. [Official ESLint 10 release](https://eslint.org/blog/2026/02/eslint-v10.0.0-released/), [official compatibility utilities](https://eslint.org/blog/2024/05/eslint-compatibility-utilities/).
- Native peer metadata for legacy React/import/accessibility plugins still advertises ESLint <=9. Clean `npm ci` reports these warnings; `npm ls --all` reports invalid peer ranges. Compatibility is supplied by the documented adapter and exercised rules, not native plugin support. No `--force`, `--legacy-peer-deps`, lowered lint severity or disabled rule is used. Reassess when native plugin support is released.
- Python direct requirements and full hashed Windows/Linux wheel locks freeze the tested graph. SQLAlchemy is on the maintained 2.0.54 line; the 2.1 migration awaits live MySQL checks. pandas 3's string dtype/copy-on-write migration awaits real CSV/report/fallback acceptance. [SQLAlchemy migration notes](https://docs.sqlalchemy.org/en/21/changelog/migration_21.html), [pandas 3 changes](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html).
- PyMySQL stays at 1.2.3 to retain the 1.2.1 security fix. PR #13's range-only proposal is superseded by the explicit exact freeze, not by a downgrade. [Official changelog](https://github.com/PyMySQL/PyMySQL/blob/main/CHANGELOG.md).
- Reviewed setup-node 7, python-dotenv 1.2.4 and Uvicorn 0.54.0 updates are retained. No API server feature flags, schema or authorization policy change.

## Source and acceptance tooling

Application, UI feature, API, service, repository, model, production SQL/seed and academic-demo files remain byte-identical to the original v2 faculty baseline. Existing tests remain unchanged except `tests/test_analytics.py`: the empty-CSV assertion now requires the exact host `os.linesep` bytes instead of hard-coding Linux LF. Windows CI observed CRLF from unchanged pandas/export code. This matches [pandas documentation](https://pandas.pydata.org/pandas-docs/version/2.3/reference/api/pandas.DataFrame.to_csv.html); it skips no test and preserves the application output. Other differences are dependency/security manifests, tooling, CI and documentation.

The Windows orchestrator had a missing closing parenthesis in its required-file check. The correction preserves its existing fail-closed behavior. Windows CI parses every PowerShell script and runs server-independent gates; it does not execute the database acceptance orchestrator or claim a laptop result. CI explicitly installs npm 11.9.0 because setup-node supplied npm 11.17.0 on the Windows runner. The audit wrapper resolves `npm.cmd` on Windows while preserving the existing exact advisory policy.

The deterministic bundle is generated from a selected Git commit, verifies every blob, excludes dependencies/build/private data, uses one versioned root and adds only `SOURCE_COMMIT.txt` distribution metadata. It exports raw Git blobs rather than checkout-filtered bytes (the existing attributes give PowerShell files CRLF in checkouts); a dirty tracked working tree is rejected. ZIP SHA-256, CRC, safe names, clean extraction with spaces and every manifest entry are checked. Separate observed reports avoid a self-hashing archive.

The publication workflow requires Windows success and 17 extracted-source gates before using its narrowly scoped job token to create the prerelease. It refuses existing-release overwrite and tag movement, then downloads and hashes every asset. GitHub's immutable-release flag and public/admin settings are separate verifications.

## Evidence limits

Runtime npm findings must be zero. The exact existing development-only GHSA-vfj7-8cjw-p6xm exception remains explicit and unchanged. No new advisory/package/severity can pass that gate.

The fresh external report records real counts, dependency versions, selected SHA, archive bytes and hashes. No successful static/CI/API-health result proves MySQL persistence or genuine human role/visual acceptance. Initial installation may require internet; execution is localhost rather than a cloud deployment.
