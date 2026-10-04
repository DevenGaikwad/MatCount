"""Static SEMS SQL-contract validation that does not require a MySQL server."""

from __future__ import annotations

import re
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = PROJECT_ROOT / "sql"
ACADEMIC_DIR = PROJECT_ROOT / "academic_demo"

EXPECTED_TABLES = {
    "lab",
    "lab_contact",
    "user",
    "user_phone",
    "component_category",
    "component",
    "storage_location",
    "inventory",
    "component_request",
    "request_item",
    "transfer",
    "transfer_item",
    "disposal_record",
}

EXPECTED_VIEWS = {
    "v_inventory_detail",
    "v_component_stock_summary",
    "v_low_stock_components",
    "v_request_progress",
    "v_transfer_detail",
    "v_overdue_returns",
    "v_disposal_summary",
}

REQUIRED_FILES = [
    "00_database_setup.sql",
    "01_schema.sql",
    "02_indexes.sql",
    "03_views.sql",
    "04_routines.sql",
    "05_triggers.sql",
    "06_seed_data.sql",
    "07_verification_queries.sql",
    "99_reset_database.sql",
]

DEMO_FILES = [
    "demo/01_constraint_demo.sql",
    "demo/02_transaction_demo.sql",
    "demo/03_index_and_explain_demo.sql",
]

ACADEMIC_SQL_FILES = [
    "00_ddl_vendor_equivalents.sql",
    "01_relational_algebra_examples.sql",
    "02_dml_and_advanced_selects.sql",
    "03_joins_aggregates.sql",
    "04_nested_correlated_queries.sql",
    "05_views_indexes_explain.sql",
    "06_stored_routines.sql",
    "07_cursor_demo.sql",
    "08_trigger_audit_demo.sql",
    "09_transactions_savepoints.sql",
    "10_concurrency_demo.sql",
    "11_deadlock_demo.sql",
    "12_dcl_roles_privileges.sql",
]

ACADEMIC_TOKEN_CONTRACT = {
    "00_ddl_vendor_equivalents.sql": [
        "sems_academic_demo",
        "AUTO_INCREMENT",
        "CREATE OR REPLACE VIEW",
    ],
    "01_relational_algebra_examples.sql": [
        "INTERSECT",
        "CROSS JOIN",
        "UNION",
        "EXCEPT",
    ],
    "02_dml_and_advanced_selects.sql": [
        "CREATE TEMPORARY TABLE",
        "INSERT INTO",
        "UPDATE",
        "DELETE FROM",
        "BETWEEN",
        "IS NULL",
    ],
    "03_joins_aggregates.sql": [
        "INNER JOIN",
        "LEFT JOIN",
        "RIGHT JOIN",
        "HAVING",
        "AVG(",
    ],
    "04_nested_correlated_queries.sql": [
        "EXISTS",
        "NOT EXISTS",
        "WITH component_stock AS",
        "DENSE_RANK() OVER",
    ],
    "05_views_indexes_explain.sql": [
        "EXPLAIN FORMAT=TREE",
        "EXPLAIN ANALYZE FORMAT=TREE",
    ],
    "06_stored_routines.sql": [
        "CREATE PROCEDURE",
        "CREATE FUNCTION",
        "IN p_lab_id",
        "OUT p_position_count",
        "CASE",
    ],
    "07_cursor_demo.sql": [
        "DECLARE stock_cursor CURSOR",
        "OPEN stock_cursor",
        "FETCH stock_cursor",
        "HANDLER FOR NOT FOUND",
        "CLOSE stock_cursor",
        "MODIFIES SQL DATA",
    ],
    "08_trigger_audit_demo.sql": [
        "ACADEMIC DEMONSTRATION ONLY",
        "CREATE TRIGGER",
        "inventory_demo_audit",
    ],
    "09_transactions_savepoints.sql": [
        "START TRANSACTION",
        "SAVEPOINT",
        "ROLLBACK TO SAVEPOINT",
        "COMMIT",
        "ROLLBACK",
    ],
    "10_concurrency_demo.sql": [
        "MANUAL TWO-SESSION DEMO",
        "SELECT quantity_available",
        "FOR UPDATE",
    ],
    "11_deadlock_demo.sql": [
        "MANUAL TWO-SESSION DEMO",
        "DEADLOCK",
        "1213",
    ],
    "12_dcl_roles_privileges.sql": [
        "CREATE ROLE",
        "CREATE USER",
        "GRANT",
        "REVOKE",
        "SHOW GRANTS",
    ],
}


def normalized_identifiers(pattern: str, text: str) -> set[str]:
    return {match.lower() for match in re.findall(pattern, text, re.IGNORECASE)}


def main() -> int:
    failures: list[str] = []

    for filename in REQUIRED_FILES + DEMO_FILES:
        path = SQL_DIR / filename
        if not path.is_file() or path.stat().st_size == 0:
            failures.append(f"missing or empty SQL file: {filename}")

    academic_readme = ACADEMIC_DIR / "README.md"
    nosql_files = [
        ACADEMIC_DIR / "nosql" / "README.md",
        ACADEMIC_DIR / "nosql" / "mongodb_demo.js",
        ACADEMIC_DIR / "nosql" / "sample_component_catalogue.json",
    ]
    for path in [academic_readme, *nosql_files]:
        if not path.is_file() or path.stat().st_size == 0:
            failures.append(
                f"missing or empty academic demonstration file: "
                f"{path.relative_to(PROJECT_ROOT)}"
            )

    academic_sql_dir = ACADEMIC_DIR / "sql"
    for filename in ACADEMIC_SQL_FILES:
        path = academic_sql_dir / filename
        if not path.is_file() or path.stat().st_size == 0:
            failures.append(f"missing or empty academic SQL file: {filename}")

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1

    schema = (SQL_DIR / "01_schema.sql").read_text(encoding="utf-8")
    views = (SQL_DIR / "03_views.sql").read_text(encoding="utf-8")
    verification = (SQL_DIR / "07_verification_queries.sql").read_text(
        encoding="utf-8"
    )
    constraint_demo = (SQL_DIR / DEMO_FILES[0]).read_text(encoding="utf-8")
    transaction_demo = (SQL_DIR / DEMO_FILES[1]).read_text(encoding="utf-8")
    explain_demo = (SQL_DIR / DEMO_FILES[2]).read_text(encoding="utf-8")

    actual_tables = normalized_identifiers(
        r"CREATE\s+TABLE\s+`?([a-z_]+)`?\s*\(", schema
    )
    actual_views = normalized_identifiers(
        r"CREATE\s+OR\s+REPLACE\s+VIEW\s+`?([a-z_]+)`?\s+AS", views
    )

    if actual_tables != EXPECTED_TABLES:
        failures.append(
            f"table boundary mismatch: expected={sorted(EXPECTED_TABLES)}, "
            f"actual={sorted(actual_tables)}"
        )
    if actual_views != EXPECTED_VIEWS:
        failures.append(
            f"view boundary mismatch: expected={sorted(EXPECTED_VIEWS)}, "
            f"actual={sorted(actual_views)}"
        )

    required_schema_tokens = [
        "ENGINE = InnoDB",
        "BIGINT UNSIGNED",
        "AUTO_INCREMENT",
        "ON UPDATE CASCADE",
        "quantity_available",
        "quantity_reserved",
        "manufacturer_details",
        "`user`",
    ]
    for token in required_schema_tokens:
        if token not in schema:
            failures.append(f"schema token missing: {token}")

    forbidden_schema_tokens = [
        "password_hash",
        "destination_inventory_id",
        "lab_status",
        "audit_log",
        "smart_electronics_lab_ddl",
    ]
    for token in forbidden_schema_tokens:
        if token.lower() in schema.lower():
            failures.append(f"forbidden schema token found: {token}")

    for token in [
        "quantity_available + i.quantity_reserved",
        "AS inventory_value",
        "COALESCE(SUM(ri.item_status = 'FULFILLED'), 0)",
    ]:
        if token.lower() not in views.lower():
            failures.append(f"view/reporting rule missing: {token}")

    for query_token in [
        "SELECT VERSION()",
        "SELECT DATABASE()",
        "SHOW TABLES",
        "SHOW INDEX FROM inventory",
        "DESCRIBE inventory",
        "v_low_stock_components",
        "v_request_progress",
        "v_transfer_detail",
        "v_overdue_returns",
        "v_disposal_summary",
        "SUM(inventory_value)",
        "total_on_hand_inventory_value",
    ]:
        if query_token.lower() not in verification.lower():
            failures.append(f"verification query missing: {query_token}")

    verification_without_comments = re.sub(
        r"--.*?$", "", verification, flags=re.MULTILINE
    )
    if re.search(
        r"\b(INSERT|UPDATE|DELETE|REPLACE|DROP|ALTER|TRUNCATE|CREATE)\b",
        verification_without_comments,
        flags=re.IGNORECASE,
    ):
        failures.append("07_verification_queries.sql must remain read-only")

    if constraint_demo.count("EXPECTED FAILURE") < 5:
        failures.append("constraint demo must label five expected failures")
    for token in ["START TRANSACTION", "ROLLBACK", "value_after_rollback"]:
        if token.lower() not in transaction_demo.lower():
            failures.append(f"transaction demo token missing: {token}")
    if len(re.findall(r"\bEXPLAIN\b", explain_demo, re.IGNORECASE)) < 4:
        failures.append("index demo must include at least four EXPLAIN statements")

    for filename, tokens in ACADEMIC_TOKEN_CONTRACT.items():
        path = academic_sql_dir / filename
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        if "-- SAFETY:" not in content:
            failures.append(f"academic SQL safety label missing: {filename}")
        for token in tokens:
            if token.lower() not in content.lower():
                failures.append(
                    f"academic SQL token missing in {filename}: {token}"
                )

    for filename in [
        "00_ddl_vendor_equivalents.sql",
        "06_stored_routines.sql",
        "07_cursor_demo.sql",
        "08_trigger_audit_demo.sql",
        "09_transactions_savepoints.sql",
        "10_concurrency_demo.sql",
        "11_deadlock_demo.sql",
    ]:
        content = (academic_sql_dir / filename).read_text(encoding="utf-8")
        if "sems_academic_demo" not in content:
            failures.append(
                f"isolated demo does not identify sems_academic_demo: {filename}"
            )

    audit_demo = (academic_sql_dir / "08_trigger_audit_demo.sql").read_text(
        encoding="utf-8"
    )
    if re.search(
        r"CREATE\s+TABLE\s+(?:sems_db\.)?`?audit",
        audit_demo,
        flags=re.IGNORECASE,
    ):
        failures.append("audit demonstration must not create a table in sems_db")

    nosql_demo = (ACADEMIC_DIR / "nosql" / "mongodb_demo.js").read_text(
        encoding="utf-8"
    )
    for token in ["insertMany", "find(", "updateOne", "deleteOne"]:
        if token not in nosql_demo:
            failures.append(f"MongoDB academic demo token missing: {token}")

    if failures:
        print("SEMS SQL contract: FAILED", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("SEMS SQL contract: PASS")
    print(f"Frozen relations: {len(actual_tables)}")
    print(f"Required reporting views: {len(actual_views)}")
    print(f"SQL scripts checked: {len(REQUIRED_FILES)}")
    print(f"Optional faculty demo scripts checked: {len(DEMO_FILES)}")
    print(f"ETCS302 academic SQL scripts checked: {len(ACADEMIC_SQL_FILES)}")
    print("Optional NoSQL academic extension: present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
