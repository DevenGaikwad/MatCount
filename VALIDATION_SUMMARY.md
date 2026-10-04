# RC2 validation boundaries

The source candidate preserves the uploaded v2 application/SQL/academic-demo contract: 13 relations, seven production views and two production triggers. The root `SOURCE_COMMIT.txt` is generated during distribution and records the exact immutable source commit.

The external `MatCount_SEMS_v2_Offline_Faculty_Demo_FINAL_v2.0.0-rc.2_VALIDATION_REPORT.md` records the ZIP hash, size, Git mapping, clean extraction and the actual gate results for those bytes. Source documentation alone is not proof that a command passed. The package builder compares every committed file with its Git blob hash and verifies every external manifest entry after extraction into a path containing spaces.

The server-independent gate runs source exclusions, SQL contract, secret scan, documentation links, pip consistency, project validation, Python/API/RBAC tests, locked npm installation, typing, lint, negative lint/runtime compatibility probes, frontend tests, the unchanged audit policy and production build. It deliberately does not configure or execute MySQL integration against `sems_db`.

Expected historical counts are 131 server-independent Python cases, 17 dedicated API cases, 30 focused security cases and 10 frontend cases. Only the external report's observed counts apply to the selected archive. Twenty MySQL cases remain excluded until a safe disposable database is configured on the intended host.

Windows CI can check parsing, dependency restoration and server-independent execution. It does not establish acceptance of the intended laptop, MySQL Server 8.4.11, Workbench/CLI proof, live four-role workflows, genuine screenshot/mobile/accessibility review or faculty approval. Those gates remain open in GitHub issues #2–#7.

The documented development-only `braces` advisory remains subject to the exact fail-on-change policy. ESLint's official compatibility adapter preserves legacy plugin rules; npm can still warn about those plugins' native peer ranges. The adapter is exercised by negative probes rather than disabling any rule. No clean audit is represented as complete security.
