"""Fail safely when release sources expose credentials or client-side DB access."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IGNORED_PARTS = {
    ".git",
    ".next",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    "logs",
    "exports",
}
SOURCE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".mjs", ".json", ".toml", ".yml", ".yaml", ".md", ".sql", ".txt"}
PLACEHOLDERS = {"replace_with", "your_", "change_me", "password", "secret", "example", "<", "${", "{"}


def _tracked_secret_files() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files"], cwd=ROOT, text=True, capture_output=True, check=False
        )
    except OSError:
        return []
    if result.returncode != 0:
        return []
    forbidden = {".env", ".streamlit/secrets.toml", "frontend/.env.local"}
    return sorted(path for path in result.stdout.splitlines() if path in forbidden)


def _source_files():
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in IGNORED_PARTS for part in path.parts):
            continue
        if path.suffix.lower() in SOURCE_SUFFIXES or path.name in {".env.example"}:
            yield path


def main() -> int:
    failures: list[str] = []
    tracked = _tracked_secret_files()
    if tracked:
        failures.extend(f"tracked private configuration: {path}" for path in tracked)

    frontend = ROOT / "frontend"
    client_forbidden = ["db_password", "database_url", "mysql+pymysql", "bcrypt", "password_hash", "sems_demo_credentials_json"]
    for path in frontend.rglob("*"):
        if not path.is_file() or any(part in IGNORED_PARTS for part in path.parts):
            continue
        if path.suffix.lower() not in SOURCE_SUFFIXES and not path.name.startswith(".env"):
            continue
        source = path.read_text(encoding="utf-8", errors="ignore").lower()
        for token in client_forbidden:
            if token in source:
                failures.append(f"private/database token in browser source: {path.relative_to(ROOT)}")
                break
        public_names = set(re.findall(r"next_public_[a-z0-9_]+", source, re.I))
        if public_names - {"next_public_sems_api_url"}:
            failures.append(f"unapproved browser environment variable: {path.relative_to(ROOT)}")

    connection_pattern = re.compile(r"mysql\+pymysql://[^:\s]+:([^@\s]+)@", re.I)
    bcrypt_pattern = re.compile(r"\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}")
    for path in _source_files():
        if "tests" in path.parts:
            continue
        source = path.read_text(encoding="utf-8", errors="ignore")
        if bcrypt_pattern.search(source):
            failures.append(f"bcrypt hash embedded in source: {path.relative_to(ROOT)}")
        for match in connection_pattern.finditer(source):
            credential = match.group(1).lower()
            if not any(marker in credential for marker in PLACEHOLDERS):
                failures.append(f"non-placeholder database URL in source: {path.relative_to(ROOT)}")

    for path in [ROOT / ".env.example", ROOT / ".streamlit/secrets.toml.example"]:
        source = path.read_text(encoding="utf-8", errors="ignore").lower()
        if "replace_with" not in source:
            failures.append(f"credential template lacks placeholders: {path.relative_to(ROOT)}")

    package = json.loads((frontend / "package.json").read_text(encoding="utf-8"))
    dependencies = {
        **package.get("dependencies", {}),
        **package.get("devDependencies", {}),
    }
    prohibited_packages = sorted(set(dependencies) & {"mysql", "mysql2", "pymysql", "sequelize", "typeorm"})
    if prohibited_packages:
        failures.append("Node database packages are prohibited: " + ", ".join(prohibited_packages))

    if failures:
        print("SEMS secret hygiene: FAILED")
        for failure in sorted(set(failures)):
            print(f"- {failure}")
        return 1
    print("SEMS secret hygiene: PASS")
    print("- private configuration files are not tracked")
    print("- browser source contains no database credentials or drivers")
    print("- templates use explicit placeholders")
    print("- no embedded bcrypt hashes or private database URLs detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
