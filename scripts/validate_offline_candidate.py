"""Run server-independent RC gates from a clean extracted source folder."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    logs = output.parent / (output.stem + "-logs")
    logs.mkdir(parents=True, exist_ok=True)
    npm = shutil.which("npm") or "npm"
    env = os.environ.copy()
    env["NEXT_TELEMETRY_DISABLED"] = "1"
    env.pop("SEMS_TEST_DATABASE_URL", None)
    checks = [
        ("source-integrity", [sys.executable, "scripts/verify_release_artifacts.py"], root),
        ("sql-contract", [sys.executable, "scripts/validate_sql_contract.py"], root),
        ("secret-scan", [sys.executable, "scripts/scan_secrets.py"], root),
        ("documentation-links", [sys.executable, "scripts/check_docs_links.py"], root),
        ("pip-check", [sys.executable, "-m", "pip", "check"], root),
        ("project-validation", [sys.executable, "scripts/validate_project.py", "--skip-tests"], root),
        ("python", [sys.executable, "-m", "pytest", "-q", "-m", "not integration"], root),
        ("api", [sys.executable, "-m", "pytest", "-q", "tests/api"], root),
        ("rbac-financial", [sys.executable, "-m", "pytest", "-q", "tests/test_data_policy.py", "tests/test_service_security.py", "tests/api/test_api_contract.py"], root),
        ("npm-ci", [npm, "ci", "--no-audit", "--no-fund"], root / "frontend"),
        ("typecheck", [npm, "run", "typecheck"], root / "frontend"),
        ("lint", [npm, "run", "lint"], root / "frontend"),
        ("tooling-compatibility", [npm, "run", "check:tooling"], root / "frontend"),
        ("frontend-tests", [npm, "run", "test"], root / "frontend"),
        ("npm-audit-policy", [sys.executable, "scripts/check_npm_audit.py"], root),
        ("production-build", [npm, "run", "build"], root / "frontend"),
        ("local-service-startup", [sys.executable, "scripts/smoke_local_services.py"], root),
    ]
    report = {
        "source_commit": (root / "SOURCE_COMMIT.txt").read_text().splitlines()[0] if (root / "SOURCE_COMMIT.txt").exists() else os.environ.get("GITHUB_SHA", "uncommitted local staging"),
        "time_utc": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "node": subprocess.check_output([shutil.which("node") or "node", "--version"], text=True).strip(),
        "npm": subprocess.check_output([npm, "--version"], text=True).strip(),
        "checks": [],
        "pending": ["intended Windows laptop", "MySQL 8.4.11 and 20 integration tests", "Workbench/CLI proof", "four-role workflows", "genuine visual/accessibility and faculty acceptance"],
    }
    validation_started = time.monotonic()
    for name, command, cwd in checks:
        print(f"Running {name}...", flush=True)
        started = time.monotonic()
        completed = subprocess.run(command, cwd=cwd, env=env, text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=900, check=False)
        log = logs / f"{name}.txt"
        log.write_text(completed.stdout, encoding="utf-8")
        report["checks"].append({"name": name, "command": command, "cwd": str(cwd), "duration_seconds": round(time.monotonic() - started, 3), "exit_code": completed.returncode, "output": completed.stdout})
        report["total_duration_seconds"] = round(time.monotonic() - validation_started, 3)
        output.write_text(json.dumps(report, indent=2), encoding="utf-8")
        if completed.returncode:
            print(f"FAIL: {name}; see {log}", flush=True)
            return 1
        print(f"PASS: {name}", flush=True)
    print("All configured server-independent candidate gates passed.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
