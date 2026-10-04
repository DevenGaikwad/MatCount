"""Student-friendly, non-destructive SEMS local readiness check."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import tomllib
from pathlib import Path
from urllib.parse import quote_plus


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "app.py",
    "requirements.txt",
    ".env.example",
    ".streamlit/secrets.toml.example",
    "sql/00_database_setup.sql",
    "sql/01_schema.sql",
    "sql/02_indexes.sql",
    "sql/03_views.sql",
    "sql/04_routines.sql",
    "sql/05_triggers.sql",
    "sql/06_seed_data.sql",
    "sql/07_verification_queries.sql",
    "sql/99_reset_database.sql",
    "api/main.py",
    "frontend/package.json",
    "frontend/package-lock.json",
    "frontend/app/login/page.tsx",
    "scripts/final_acceptance.ps1",
    "scripts/scan_secrets.py",
]
PACKAGE_IMPORTS = {
    "streamlit": "streamlit",
    "SQLAlchemy": "sqlalchemy",
    "PyMySQL": "pymysql",
    "pandas": "pandas",
    "Plotly": "plotly",
    "python-dotenv": "dotenv",
    "bcrypt": "bcrypt",
    "pytest": "pytest",
    "FastAPI": "fastapi",
    "Uvicorn": "uvicorn",
    "HTTPX": "httpx",
}
PLACEHOLDER_MARKERS = ("REPLACE_WITH", "YOUR_", "CHANGE_ME")


class Results:
    def __init__(self) -> None:
        self.failures = 0

    def pass_(self, message: str) -> None:
        print(f"[PASS] {message}")

    def fail(self, message: str) -> None:
        self.failures += 1
        print(f"[FAIL] {message}")

    def skip(self, message: str) -> None:
        print(f"[SKIP] {message}")


def _dotenv_values(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def _active_configuration() -> dict[str, str]:
    values = _dotenv_values(ROOT / ".env")
    for key in ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]:
        if key in os.environ:
            values[key] = os.environ[key]

    secrets_path = ROOT / ".streamlit/secrets.toml"
    if secrets_path.is_file():
        try:
            database = tomllib.loads(
                secrets_path.read_text(encoding="utf-8")
            ).get("database", {})
        except (OSError, tomllib.TOMLDecodeError):
            database = {}
        for key, secret_key in {
            "DB_HOST": "host",
            "DB_PORT": "port",
            "DB_NAME": "name",
            "DB_USER": "user",
            "DB_PASSWORD": "password",
        }.items():
            if key not in values and secret_key in database:
                values[key] = str(database[secret_key])
    return values


def _configuration_issues(values: dict[str, str]) -> list[str]:
    issues: list[str] = []
    for key in ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]:
        value = values.get(key, "").strip()
        if not value or any(marker in value for marker in PLACEHOLDER_MARKERS):
            issues.append(f"{key} is missing or still a placeholder")
    if values.get("DB_NAME") and values["DB_NAME"] != "sems_db":
        issues.append("DB_NAME must be sems_db")
    try:
        port = int(values.get("DB_PORT", ""))
        if not 1 <= port <= 65535:
            raise ValueError
    except ValueError:
        if "DB_PORT is missing or still a placeholder" not in issues:
            issues.append("DB_PORT must be a number between 1 and 65535")
    return issues


def _check_database(results: Results, values: dict[str, str]) -> None:
    try:
        from sqlalchemy import create_engine, text

        url = (
            "mysql+pymysql://"
            f"{quote_plus(values['DB_USER'])}:{quote_plus(values['DB_PASSWORD'])}"
            f"@{values['DB_HOST']}:{int(values['DB_PORT'])}/"
            f"{values['DB_NAME']}?charset=utf8mb4"
        )
        engine = create_engine(
            url,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 3},
            future=True,
        )
        with engine.connect() as connection:
            row = connection.execute(
                text("SELECT VERSION(), DATABASE()")
            ).one()
        engine.dispose()
        if not str(row[0]).startswith("8.4.") or row[1] != "sems_db":
            results.fail("Connected server/database is not MySQL 8.4.x / sems_db")
        else:
            results.pass_(f"MySQL {row[0]} connection to sems_db")
    except Exception as exc:
        results.fail(f"MySQL health check unavailable ({exc.__class__.__name__})")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-database", action="store_true", help="Do not attempt a live connection"
    )
    parser.add_argument(
        "--allow-unconfigured",
        action="store_true",
        help="Treat absent local credentials as an expected repository state",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    results = Results()

    if sys.version_info >= (3, 12):
        results.pass_(f"Python {sys.version_info.major}.{sys.version_info.minor}+")
    else:
        results.fail("Python 3.12 or later is required")

    missing = [name for name in REQUIRED_FILES if not (ROOT / name).is_file()]
    if missing:
        results.fail("Required project files missing: " + ", ".join(missing))
    else:
        results.pass_(f"Required project files present ({len(REQUIRED_FILES)})")

    sql_files = list((ROOT / "sql").glob("*.sql"))
    if len(sql_files) >= 9:
        results.pass_("Numbered SQL foundation/support scripts present")
    else:
        results.fail("One or more numbered SQL scripts are missing")

    missing_packages = [
        name
        for name, module in PACKAGE_IMPORTS.items()
        if importlib.util.find_spec(module) is None
    ]
    if missing_packages:
        results.fail("Required package imports missing: " + ", ".join(missing_packages))
    else:
        results.pass_(f"Required package imports available ({len(PACKAGE_IMPORTS)})")

    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    if ".env" in gitignore and ".streamlit/secrets.toml" in gitignore:
        results.pass_("Local credential files are Git-ignored")
    else:
        results.fail(".gitignore does not protect all local credential files")

    templates = [ROOT / ".env.example", ROOT / ".streamlit/secrets.toml.example"]
    if all(any(marker in path.read_text(encoding="utf-8") for marker in PLACEHOLDER_MARKERS) for path in templates):
        results.pass_("Configuration templates contain placeholders, not active secrets")
    else:
        results.fail("A configuration template lacks an explicit placeholder")

    values = _active_configuration()
    config_issues = _configuration_issues(values)
    if config_issues:
        if args.allow_unconfigured:
            results.skip("Local DB configuration not supplied; repository templates are ready")
        else:
            for issue in config_issues:
                results.fail(issue)
    else:
        results.pass_("DB_HOST/PORT/NAME/USER/PASSWORD configured")
        credentials_json = os.getenv("SEMS_DEMO_CREDENTIALS_JSON")
        if credentials_json:
            try:
                if not isinstance(json.loads(credentials_json), dict):
                    raise ValueError
                results.pass_("External demonstration credential map is valid JSON")
            except (json.JSONDecodeError, ValueError):
                results.fail("SEMS_DEMO_CREDENTIALS_JSON must be a JSON object")
        if args.skip_database:
            results.skip("Live MySQL health check disabled by command option")
        elif not missing_packages:
            _check_database(results, values)

    print(f"Preflight result: {'PASS' if results.failures == 0 else 'FAIL'}")
    return 0 if results.failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
