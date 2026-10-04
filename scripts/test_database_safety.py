"""Validate the dedicated integration database target without exposing its URL."""

from __future__ import annotations

import os
from urllib.parse import urlsplit


def target_database(url_text: str) -> str:
    return urlsplit(url_text).path.lstrip("/").split("/", 1)[0] if url_text else ""


def validate_test_target(url_text: str) -> tuple[bool, str]:
    database = target_database(url_text)
    if not database:
        return False, "SEMS_TEST_DATABASE_URL is not configured."
    if database == "sems_db" or not database.endswith("_test"):
        return False, "Integration target must end in _test and must never be sems_db."
    return True, f"Dedicated integration target is safely named {database}."


def main() -> int:
    safe, message = validate_test_target(os.getenv("SEMS_TEST_DATABASE_URL", ""))
    print(f"[{'PASS' if safe else 'FAIL'}] {message}")
    return 0 if safe else 1


if __name__ == "__main__":
    raise SystemExit(main())
