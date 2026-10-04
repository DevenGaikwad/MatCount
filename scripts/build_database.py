"""Execute SEMS SQL files against sems_db or a dedicated *_test database."""

from __future__ import annotations

import argparse
import getpass
import os
import re
from collections.abc import Iterator
from pathlib import Path

import pymysql


ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = ROOT / "sql"
BUILD_FILES = [
    "00_database_setup.sql",
    "01_schema.sql",
    "02_indexes.sql",
    "03_views.sql",
    "04_routines.sql",
    "05_triggers.sql",
    "06_seed_data.sql",
]


def validate_database_name(name: str) -> str:
    if not re.fullmatch(r"[a-z][a-z0-9_]{2,63}", name):
        raise ValueError("Database name contains unsupported characters.")
    if name != "sems_db" and not name.endswith("_test"):
        raise ValueError("Target must be sems_db or a dedicated database ending in _test.")
    return name


def target_script(text: str, database: str) -> str:
    validate_database_name(database)
    if database == "sems_db":
        return text
    return text.replace("CREATE DATABASE IF NOT EXISTS sems_db", f"CREATE DATABASE IF NOT EXISTS {database}").replace(
        "USE sems_db;", f"USE {database};"
    )


def split_mysql_script(text: str) -> Iterator[str]:
    delimiter = ";"
    buffer: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not buffer and (not stripped or stripped.startswith("--") or stripped.startswith("#")):
            continue
        if stripped.upper().startswith("DELIMITER "):
            if "\n".join(buffer).strip():
                raise ValueError("DELIMITER changed while a SQL statement was incomplete.")
            delimiter = stripped.split(maxsplit=1)[1]
            continue
        buffer.append(line)
        current = "\n".join(buffer).rstrip()
        if current.endswith(delimiter):
            statement = current[: -len(delimiter)].strip()
            buffer = []
            if statement:
                yield statement
    remainder = "\n".join(buffer).strip()
    if remainder and not all(
        not row.strip() or row.strip().startswith(("--", "#"))
        for row in remainder.splitlines()
    ):
        raise ValueError("SQL script ended with an incomplete statement.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", default=os.getenv("DB_NAME", "sems_db"))
    parser.add_argument("--host", default=os.getenv("DB_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("DB_PORT", "3306")))
    parser.add_argument("--user", default=os.getenv("DB_USER", "root"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    database = validate_database_name(args.database)
    if not 1 <= args.port <= 65535:
        raise ValueError("MySQL port must be between 1 and 65535.")
    password = os.getenv("DB_PASSWORD") or getpass.getpass(
        f"MySQL password for {args.user}@{args.host}: "
    )
    connection = pymysql.connect(
        host=args.host,
        port=args.port,
        user=args.user,
        password=password,
        charset="utf8mb4",
        connect_timeout=5,
        autocommit=False,
    )
    try:
        with connection.cursor() as cursor:
            for filename in BUILD_FILES:
                source = (SQL_DIR / filename).read_text(encoding="utf-8")
                source = target_script(source, database)
                for number, statement in enumerate(split_mysql_script(source), start=1):
                    try:
                        cursor.execute(statement)
                        if cursor.description:
                            cursor.fetchall()
                    except Exception as exc:
                        connection.rollback()
                        raise RuntimeError(
                            f"{filename}, statement {number} failed: {exc}"
                        ) from exc
                connection.commit()
                print(f"OK  {filename}")
        print(f"SEMS database build complete: {database}")
        return 0
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
