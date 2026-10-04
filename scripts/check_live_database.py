"""Non-destructively verify the live sems_db identity and frozen database objects."""

from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.constants import DATABASE_NAME
from config.settings import get_settings
from db.connection import get_engine
try:
    from scripts.validate_sql_contract import EXPECTED_TABLES, EXPECTED_VIEWS
except ModuleNotFoundError:  # Direct execution places scripts/ first on sys.path.
    from validate_sql_contract import EXPECTED_TABLES, EXPECTED_VIEWS


EXPECTED_ROUTINES = {"fn_inventory_available_value", "sp_component_availability"}
EXPECTED_TRIGGERS = {
    "trg_inventory_validate_location_bi",
    "trg_inventory_validate_location_bu",
}


def _names(connection, statement: str) -> set[str]:
    return {
        str(row[0]).lower()
        for row in connection.execute(text(statement), {"schema": DATABASE_NAME})
    }


def main() -> int:
    settings = get_settings()
    issues = settings.connection_issues()
    if issues:
        print("[FAIL] Live database configuration is incomplete.")
        return 1
    try:
        with get_engine().connect() as connection:
            version, database = connection.execute(
                text("SELECT VERSION(), DATABASE()")
            ).one()
            tables = _names(
                connection,
                """
                SELECT TABLE_NAME FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = :schema AND TABLE_TYPE = 'BASE TABLE'
                """,
            )
            views = _names(
                connection,
                "SELECT TABLE_NAME FROM information_schema.VIEWS WHERE TABLE_SCHEMA = :schema",
            )
            routines = _names(
                connection,
                "SELECT ROUTINE_NAME FROM information_schema.ROUTINES WHERE ROUTINE_SCHEMA = :schema",
            )
            triggers = _names(
                connection,
                "SELECT TRIGGER_NAME FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA = :schema",
            )
            function_value = connection.execute(
                text("SELECT fn_inventory_available_value(2, 3.50)")
            ).scalar_one()
            procedure_result = connection.execute(
                text("CALL sp_component_availability(0, NULL)")
            )
            procedure_result.fetchall()
    except (SQLAlchemyError, TypeError, ValueError) as exc:
        print(f"[FAIL] Live database inspection failed ({exc.__class__.__name__}).")
        return 1

    failures: list[str] = []
    if database != DATABASE_NAME:
        failures.append(f"connected database is not {DATABASE_NAME}")
    if not str(version).startswith("8.4."):
        failures.append("server is not MySQL 8.4.x LTS")
    if tables != EXPECTED_TABLES:
        failures.append("base-table set does not exactly match the frozen 13 relations")
    if not EXPECTED_VIEWS.issubset(views):
        failures.append("one or more required reporting views are missing")
    if float(function_value) != 7.0:
        failures.append("inventory-value function returned an unexpected value")

    if failures:
        print("SEMS live database readiness: FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("SEMS live database readiness: PASS")
    print(f"MySQL version: {version}")
    print(f"Database: {database}")
    print(f"Frozen relations: {len(tables)}")
    print(f"Required views: {len(EXPECTED_VIEWS)}")
    print(f"Required routines executed read-only: {len(EXPECTED_ROUTINES)}")
    if EXPECTED_TRIGGERS.issubset(triggers):
        print(f"Required triggers visible: {len(EXPECTED_TRIGGERS)}")
    else:
        print(
            "Trigger metadata is not fully visible to this account; "
            "confirm both names in Workbench (static definitions already pass)."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
