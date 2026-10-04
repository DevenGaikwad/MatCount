"""Gate runtime npm advisories and narrowly document one unfixed dev-only chain."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


FRONTEND = Path(__file__).resolve().parents[1] / "frontend"
ADVISORY = "https://github.com/advisories/GHSA-vfj7-8cjw-p6xm"
KNOWN_CHAIN = {
    "braces",
    "micromatch",
    "fast-glob",
    "@next/eslint-plugin-next",
    "eslint-config-next",
}


def audit(*args: str) -> dict:
    result = subprocess.run(
        ["npm", "audit", "--json", *args],
        cwd=FRONTEND,
        text=True,
        capture_output=True,
        check=False,
        timeout=180,
    )
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError(f"npm audit did not return valid JSON (exit {result.returncode})") from exc
    if result.returncode not in (0, 1) or report.get("error"):
        raise ValueError(f"npm audit could not complete (exit {result.returncode})")
    return report


def check() -> None:
    runtime = audit("--omit=dev")
    counts = runtime.get("metadata", {}).get("vulnerabilities", {})
    if counts.get("total") != 0:
        raise ValueError(f"runtime dependency audit has {counts.get('total', 'unknown')} findings")
    print("npm runtime audit: PASS (zero findings)")

    full = audit()
    findings = full.get("vulnerabilities", {})
    if not findings:
        print("npm full audit: PASS (zero findings)")
        return
    if not set(findings).issubset(KNOWN_CHAIN) or "braces" not in findings:
        raise ValueError("npm full audit includes an unreviewed affected package")
    direct_advisories: set[str] = set()
    for name, detail in findings.items():
        if detail.get("severity") != "high":
            raise ValueError(f"unreviewed severity in npm audit: {name}")
        if detail.get("isDirect") and name != "eslint-config-next":
            raise ValueError(f"unexpected direct dependency in npm audit: {name}")
        for via in detail.get("via", []):
            if isinstance(via, str):
                if via not in KNOWN_CHAIN:
                    raise ValueError(f"unreviewed dependency chain for {name}")
            elif isinstance(via, dict):
                direct_advisories.add(via.get("url", ""))
            else:
                raise ValueError(f"unreadable advisory entry for {name}")
    if direct_advisories != {ADVISORY}:
        raise ValueError("npm audit advisory set changed; review before publication")
    print(
        "npm full audit: documented dev-only exception "
        f"{ADVISORY} ({len(findings)} affected packages; no upstream fix)"
    )
    print("Any additional advisory, package, or runtime finding fails this gate.")


def main() -> int:
    try:
        check()
        return 0
    except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
        print(f"npm audit gate: FAIL ({exc})", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
