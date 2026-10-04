"""Run the non-destructive SEMS validation sequence with one command."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

try:
    from scripts.test_database_safety import validate_test_target
except ModuleNotFoundError:  # Direct execution places scripts/ first on sys.path.
    from test_database_safety import validate_test_target


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--local-acceptance",
        action="store_true",
        help="Require active DB configuration and include the live preflight health check",
    )
    parser.add_argument("--skip-tests", action="store_true")
    return parser.parse_args()


def run_check(label: str, command: list[str]) -> bool:
    print(f"\n=== {label} ===")
    completed = subprocess.run(command, cwd=ROOT, check=False)
    print(f"[{ 'PASS' if completed.returncode == 0 else 'FAIL' }] {label}")
    return completed.returncode == 0


def integration_target_is_safe() -> bool:
    safe, message = validate_test_target(os.getenv("SEMS_TEST_DATABASE_URL", ""))
    print(f"[{'PASS' if safe else 'FAIL'}] {message}")
    return safe


def main() -> int:
    args = parse_args()
    python = sys.executable
    checks: list[bool] = []
    checks.append(
        run_check(
            "Python compile check",
            [
                python,
                "-m",
                "compileall",
                "-q",
                "app.py",
                "config",
                "db",
                "repositories",
                "services",
                "ui",
                "pages",
                "api",
                "scripts",
                "tests",
            ],
        )
    )
    checks.append(
        run_check("SQL static contract", [python, "scripts/validate_sql_contract.py"])
    )
    checks.append(
        run_check("Secret hygiene", [python, "scripts/scan_secrets.py"])
    )

    preflight = [python, "scripts/preflight_check.py"]
    if args.local_acceptance:
        preflight.extend([])
    else:
        preflight.extend(["--allow-unconfigured", "--skip-database"])
    checks.append(run_check("Local readiness preflight", preflight))

    integration_ready = True
    if args.local_acceptance:
        print("\n=== Integration target safety ===")
        integration_ready = integration_target_is_safe()
        checks.append(integration_ready)

    if not args.skip_tests and integration_ready:
        pytest_command = [python, "-m", "pytest", "-q"]
        if not args.local_acceptance:
            pytest_command[3:3] = ["-m", "not integration"]
        checks.append(
            run_check(
                "Full pytest" if args.local_acceptance else "Server-independent pytest",
                pytest_command,
            )
        )

    passed = sum(checks)
    print(f"\nSEMS validation summary: {passed}/{len(checks)} checks passed")
    return 0 if all(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
