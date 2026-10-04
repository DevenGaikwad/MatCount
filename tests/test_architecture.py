"""Repository structure and layer-boundary tests."""

import ast
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.architecture


def imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def test_required_streamlit_pages_exist() -> None:
    expected = {
        "01_Dashboard.py",
        "02_Laboratories.py",
        "03_Users.py",
        "04_Component_Catalogue.py",
        "05_Storage_Locations.py",
        "06_Inventory.py",
        "07_Component_Requests.py",
        "08_Transfers.py",
        "09_Disposal.py",
        "10_Reports.py",
    }
    assert {path.name for path in (ROOT / "pages").glob("*.py")} == expected


def test_pages_contain_no_raw_sql_or_repository_imports() -> None:
    for path in (ROOT / "pages").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported = imports(path)
        assert "sqlalchemy" not in imported
        assert not any(name.startswith("repositories") for name in imported)
        assert not any(
            isinstance(node, ast.Attribute) and node.attr in {"execute", "exec_driver_sql"}
            for node in ast.walk(tree)
        )


def test_services_do_not_import_streamlit() -> None:
    for path in (ROOT / "services").glob("*.py"):
        assert "streamlit" not in imports(path)


def test_repository_layer_does_not_import_ui_or_services() -> None:
    for path in (ROOT / "repositories").glob("*.py"):
        imported = imports(path)
        assert not any(
            name == "streamlit" or name.startswith("ui") or name.startswith("services")
            for name in imported
        )


def test_secret_templates_do_not_contain_real_passwords() -> None:
    for path in [ROOT / ".env.example", ROOT / ".streamlit/secrets.toml.example"]:
        text = path.read_text(encoding="utf-8")
        assert "REPLACE_WITH" in text
        assert "root_password" not in text.lower()


def test_thin_api_does_not_bypass_service_layer() -> None:
    forbidden = {"sqlalchemy", "pymysql", "repositories", "db"}
    for path in (ROOT / "api").rglob("*.py"):
        imported = imports(path)
        assert not any(
            name in forbidden or any(name.startswith(f"{prefix}.") for prefix in forbidden)
            for name in imported
        ), f"Transport layer bypass in {path.relative_to(ROOT)}"


def test_professional_frontend_routes_and_streamlit_fallback_coexist() -> None:
    expected_routes = {
        "dashboard",
        "laboratories",
        "users",
        "components",
        "storage-locations",
        "inventory",
        "requests",
        "transfers",
        "disposal",
        "reports",
    }
    portal = ROOT / "frontend/app/(portal)"
    assert {path.parent.name for path in portal.glob("*/page.tsx")} == expected_routes
    assert (ROOT / "app.py").is_file()
    assert (ROOT / "pages/01_Dashboard.py").is_file()


def test_node_frontend_has_no_database_driver_or_private_configuration() -> None:
    package = (ROOT / "frontend/package.json").read_text(encoding="utf-8").lower()
    assert not any(driver in package for driver in ["mysql2", "pymysql", "sqlalchemy"])
    for path in (ROOT / "frontend").rglob("*"):
        if (
            not path.is_file()
            or any(part in {"node_modules", ".next"} for part in path.parts)
            or path.suffix not in {".ts", ".tsx", ".js", ".mjs"}
        ):
            continue
        source = path.read_text(encoding="utf-8").lower()
        assert "db_password" not in source
        assert "database_url" not in source
        assert "bcrypt" not in source


def test_modernization_acceptance_files_exist() -> None:
    for relative in [
        "api/main.py",
        "frontend/package.json",
        "docs/FRONTEND_MODERNIZATION_AUDIT.md",
        "scripts/final_acceptance.ps1",
    ]:
        assert (ROOT / relative).is_file(), relative


def test_final_acceptance_is_non_destructive_and_complete() -> None:
    source = (ROOT / "scripts/final_acceptance.ps1").read_text(
        encoding="utf-8"
    ).lower()
    for prohibited in [
        "scripts/build_database.py",
        "99_reset_database.sql",
        "06_seed_data.sql",
        "drop database",
        "truncate table",
        "remove-item",
    ]:
        assert prohibited not in source
    for required in [
        "scripts/check_live_database.py",
        "scripts/test_database_safety.py",
        "python backend tests",
        "fastapi authentication / rbac / contract tests",
        "frontend type-check",
        "frontend lint",
        "frontend tests",
        "production frontend build",
        "scripts/scan_secrets.py",
        "final result: pass",
        "final result: fail",
    ]:
        assert required in source
