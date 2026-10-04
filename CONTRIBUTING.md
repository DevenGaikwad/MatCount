# Contributing to MatCount

MatCount/SEMS is an academic release candidate. Coordinate substantive changes through issues and reviewed pull requests. Suggested branches: `docs/<topic>`, `fix/<topic>`, `test/<topic>`, `release/<topic>`. Use descriptive conventional commits (for example `docs: clarify Workbench verification`) but never create artificial commits for attribution.

## Before proposing a change

1. Preserve exactly 13 production relations and seven production views. No new production table, view, column, trigger or altered workflow invariant without explicit baseline authorization; isolated `sems_academic_demo` teaching objects are not production schema.
2. Keep MySQL 8.4 compatibility and the SQL execution order `sql/00` through `sql/07`. Never point tests or disposable demonstrations at `sems_db`; integration uses only a dedicated database whose name ends in `_test`.
3. Keep authorization, scope, transaction and financial-data rules in the backend. Browser code must not contain a MySQL driver, credentials or cost/valuation fields sent to unauthorized roles.
4. Do not commit `.env`, Streamlit secrets, database dumps, production records, private hashes, access tokens, local logs, screenshots with sensitive information, generated dependencies or build outputs. Use sanitized examples and synthetic data.
5. Run `python scripts/validate_sql_contract.py`, `python scripts/scan_secrets.py`, `python scripts/validate_project.py` in a configured Python 3.12 environment; run `npm ci`, `npm run typecheck`, `npm run lint`, `npm run test`, `npm run build` in `frontend/`. Record environment and failures honestly. The Windows/MySQL gate is `.\scripts\final_acceptance.ps1` with a guarded `sems_test`.
6. Document behavioral and academic changes in the relevant `docs/` files, link to existing material rather than duplicating it, and include migration/rollback implications. No new license or institutional endorsement can be inferred.

Pull requests should state purpose, schema/view impact, RBAC/privacy impact, test evidence and acceptance limitations. Attach only genuine, sanitized screenshots, explicitly marked with capture environment/date; pending placeholders are not proof. A contribution under another person's name or a co-author trailer without actual participation is prohibited.
