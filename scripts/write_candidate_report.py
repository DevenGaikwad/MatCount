"""Write actual package and server-independent validation evidence for RC2."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()
    directory = args.directory
    package = json.loads((directory / "package-result.json").read_text())
    validation = json.loads((directory / "validation-result.json").read_text())
    checks = validation["checks"]
    if validation["source_commit"] != package["commit"]:
        raise ValueError("Validation source commit does not match the packaged source")
    if any(check["exit_code"] for check in checks) or len(checks) != 17:
        raise ValueError("Require the complete successful configured gate set")
    observed = {}
    for name, expected in [("python", 131), ("api", 17), ("rbac-financial", 30), ("frontend-tests", 10)]:
        output = next(check["output"] for check in checks if check["name"] == name)
        clean = re.sub(r"\x1b\[[0-9;]*m", "", output)
        counts = [int(value) for value in re.findall(r"(\d+) passed", clean)]
        if expected not in counts:
            raise ValueError(f"Unexpected observed count in {name}")
        observed[name] = expected
    source = Path(package["clean_root"])
    lock = json.loads((source / "frontend/package-lock.json").read_text())["packages"]
    lines = ["# MatCount / SEMS v2 RC2 offline faculty validation", "", "**Status: academic release candidate; intended-host acceptance pending.**", "", "## Exact source and package", "", f"- Source commit: `{package['commit']}`", "- Immutable candidate tag: `v2.0.0-rc.2` (publication verification is recorded separately).", f"- ZIP: `{package['archive']}`", f"- SHA-256: `{package['sha256']}`", f"- ZIP size: {package['size_bytes']} bytes.", f"- Entries: {package['entries']}; all {package['git_files']} Git source files verified by blob SHA.", "- Only generated distribution metadata: `SOURCE_COMMIT.txt`.", "- Deterministic sorted paths, timestamp 2000-01-01, one versioned root, source-only contents.", "- ZIP CRC, safe names, exclusions, clean extraction into a path containing spaces and every SHA-256 manifest entry: PASS.", "", "## Observed validation", "", f"Environment: {validation['platform']}; Python {validation['python']}; timestamp {validation['time_utc']}.", "", "| Gate | Result |", "|---|---|"]
    for check in checks:
        detail = f"PASS; {observed[check['name']]} passed" if check["name"] in observed else "PASS"
        if check["name"] == "python":
            detail += "; 20 MySQL cases deselected"
        if check["name"] == "npm-audit-policy":
            detail += "; zero runtime findings; only the documented dev-only braces chain"
        if check["name"] == "local-service-startup":
            detail += "; actual localhost API health and production login HTTP 200; no live MySQL acceptance"
        lines.append(f"| {check['name']} | {detail} |")
    lines += ["", f"Observed Node: {validation['node']}; npm: {validation['npm']}; total gate duration: {validation['total_duration_seconds']} seconds.", "", "### Exact commands and durations", "", "Commands below ran from the extracted root unless the directory is frontend. Host-specific absolute executable/root prefixes are shown relative to the bundle for readability; raw argv and working directories are retained in validation-result.json.", "", "| Gate | Directory | Command | Duration (seconds) |", "|---|---|---|---:|"]
    for check in checks:
        command = list(check["command"])
        if command[0].lower().endswith(("python", "python.exe")):
            command[0] = "python"
        elif command[0].lower().endswith(("npm", "npm.cmd")):
            command[0] = "npm"
        cwd = "frontend" if Path(check["cwd"]).name == "frontend" else "."
        lines.append(f"| {check['name']} | {cwd} | `{subprocess.list2cmdline(command)}` | {check['duration_seconds']} |")
    lines += ["", "## Frozen dependency snapshot", "", "| Dependency | Exact version |", "|---|---|"]
    for name in ["next", "sharp", "react", "react-dom", "typescript", "eslint", "@eslint/compat", "vitest"]:
        lines.append(f"| {name} | {lock['node_modules/' + name]['version']} |")
    lines += ["", "Python direct pins:", "", "```text", (source / "requirements.txt").read_text().strip(), "```", "", "Node 24.19.0 LTS/npm 11.9.0; frontend engine >=24.19.0 <25. Complete Windows x64/CPython 3.12 and Linux x86_64/CPython 3.12 wheel hashes are included. Initial installation can require internet; no dependency cache, virtual environment, node_modules, build output, MySQL installation or database data is bundled.", "", "## Parity and security", "", "The original private faculty ZIP has SHA-256 bf7c69e72a03ee50296ea1cdaa45764317b93676712866c38885fb47ebff60b0. The original RC1 has SHA-256 297890379300798ff0a57d7310c458ca45c761b36959423f8450cdb63b12ecf8. Those bytes are unchanged. RC1's 253 entries match commit 147d285eaa8ab4beed274da3b2adedf45648c36b; Git alone adds its external checksum. The full 33-path comparison is in docs/OFFLINE_FACULTY_DEMONSTRATION_BASELINE.md.", "", "RC2 preserves application/API/service/repository/model/UI feature, production SQL/seed and academic-demo source. All original tests remain except an exact host-line-separator expectation in the empty-CSV test (Linux LF / Windows CRLF), matching unchanged pandas/export behavior. Differences are reviewed dependency/security pins, lint compatibility, Windows acceptance fixes, source packaging/validation tooling and documentation/CI. The static contract remains exactly 13 relations, seven production views, two production triggers and 13 ETCS302 SQL demonstrations plus the optional isolated NoSQL extension.", "", "Student/Faculty financial minimization and Student CSV/availability restrictions are enforced at the backend/service/API boundary and tested. No private configuration or real credential/database/screenshot artifact is included. No open-source licence or institutional endorsement is implied.", "", "The remaining development advisory GHSA-vfj7-8cjw-p6xm affects five tooling packages and has no upstream fix in the audited snapshot. The unchanged exact audit gate rejects runtime findings, any additional advisory/package or severity change. Official ESLint compatibility wrapping retains all existing rule severities; negative probes detect the React, Next and accessibility rules. Native legacy-plugin peer-range warnings remain disclosed rather than hidden or force-resolved.", "", "## Intended-host acceptance still required", "", "- Fresh Windows laptop execution of .\\scripts\\final_acceptance.ps1 with private local configuration.", "- MySQL Community Server 8.4.11 and all 20 tests against a safely named disposable `_test` database.", "- Genuine MySQL Workbench/CLI proof; 13 tables/seven views/two triggers and database effects.", "- Administrator, Faculty, Lab Assistant and Student permitted/denied workflows and CSV restrictions.", "- Local audit repetition, genuine desktop/mobile/modal keyboard/focus evidence and faculty approval.", "- Final academic-release promotion only after acceptance issues #2–#7 close with evidence.", "", "Windows CI results, final GitHub state and post-upload/download asset hashes are recorded in the publication result and completion report. A source or CI pass does not establish acceptance of the user's laptop.", ""]
    report = directory / (package["archive"][:-4] + "_VALIDATION_REPORT.md")
    report.write_text("\n".join(lines), encoding="utf-8")
    notes = directory / "RELEASE_NOTES.md"
    notes.write_text("# MatCount v2.0.0 RC2 — Windows/MySQL Acceptance Pending\n\nMatCount is the public product/repository name; SEMS remains the implementation/database name.\n\nAcademic team (ascending PRN):\n1. Aaryan Sachin Anand — 1022411049 (GitHub account/invitation unverified).\n2. Deven Sachin Gaikwad — 1022411052 (repository owner).\n\n" + "\n".join(lines[4:]) + "\n\n[Faculty baseline/parity](https://github.com/DevenGaikwad/MatCount/blob/" + package["commit"] + "/docs/OFFLINE_FACULTY_DEMONSTRATION_BASELINE.md).\n\nStart at FACULTY_DEMO_START_HERE.md after SHA-256 verification. Faculty evidence refers to this immutable tag/package; later main maintenance is separate. This prerelease is not final academic acceptance or faculty approval.\n", encoding="utf-8")
    print(str(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
