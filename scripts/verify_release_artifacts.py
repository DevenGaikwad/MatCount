"""Verify the immutable v2 archive and safe repository publication inputs."""

from __future__ import annotations

import argparse
import hashlib
import re
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_NAME = "SEMS_Final_Academic_Professional_Release_v2.zip"
ORIGINAL_SHA256 = "bf7c69e72a03ee50296ea1cdaa45764317b93676712866c38885fb47ebff60b0"
CANDIDATE_NAME = "MatCount_SEMS_v2_Academic_Release_Candidate_RC1.zip"
MAX_TOTAL_SIZE = 64 * 1024 * 1024
MAX_ENTRIES = 5000
FORBIDDEN_PARTS = {
    ".git", ".venv", "node_modules", ".next", "__pycache__", ".pytest_cache",
    "secrets", "private",
}
FORBIDDEN_FILES = {".env", "secrets.toml", ".env.local"}
ALLOWED_TEMPLATES = {".env.example", ".env.local.example", "secrets.toml.example"}
FORBIDDEN_SUFFIXES = (".sqlite", ".sqlite3", ".db", ".bak", ".sql.gz")


def read_manifest(path: Path, name: str) -> str:
    line = path.read_text(encoding="ascii").strip()
    match = re.fullmatch(r"([a-f0-9]{64})  ([^/\\\s]+)", line)
    if not match or match.group(2) != name:
        raise ValueError(f"invalid release checksum manifest for {name}")
    return match.group(1)


def check_manifests() -> None:
    original = ROOT / "release" / f"{ORIGINAL_NAME}.sha256"
    if read_manifest(original, ORIGINAL_NAME) != ORIGINAL_SHA256:
        raise ValueError("committed original-v2 checksum has changed")
    candidate = ROOT / "release" / f"{CANDIDATE_NAME}.sha256"
    if candidate.exists():
        read_manifest(candidate, CANDIDATE_NAME)


def check_source() -> None:
    required = (
        "sql/00_database_setup.sql", "sql/01_schema.sql", "sql/03_views.sql",
        "sql/07_verification_queries.sql", "scripts/validate_sql_contract.py",
        "scripts/final_acceptance.ps1", "frontend/package-lock.json",
        "docs/ETCS302_SYLLABUS_TRACEABILITY_MATRIX.md",
    )
    missing = [name for name in required if not (ROOT / name).is_file()]
    if missing:
        raise ValueError("required source files absent: " + ", ".join(missing))
    for candidate in ROOT.rglob("*"):
        if not candidate.is_file() or any(part in FORBIDDEN_PARTS for part in candidate.relative_to(ROOT).parts):
            continue
        name = candidate.name
        if (
            name in FORBIDDEN_FILES
            or (name.startswith(".env.") and name not in ALLOWED_TEMPLATES)
            or (name.startswith("secrets.toml.") and name not in ALLOWED_TEMPLATES)
        ):
            raise ValueError(f"private configuration present in publication tree: {candidate.relative_to(ROOT)}")
    for name in ("frontend/node_modules", "frontend/.next", ".venv"):
        if (ROOT / name).exists():
            raise ValueError(f"generated dependency/build tree present: {name}")


def check_archive(path: Path, external_manifest: Path | None) -> None:
    if not path.is_file() or path.name not in {ORIGINAL_NAME, CANDIDATE_NAME}:
        raise ValueError("provide the named original v2 or reviewed MatCount RC1 archive")
    manifest = external_manifest or ROOT / "release" / f"{path.name}.sha256"
    expected = read_manifest(manifest, path.name)
    if path.name == ORIGINAL_NAME and expected != ORIGINAL_SHA256:
        raise ValueError("original-v2 checksum has changed")
    with path.open("rb") as source:
        digest = hashlib.file_digest(source, "sha256").hexdigest()
    if digest != expected:
        raise ValueError("archive SHA-256 mismatch; do not publish")
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        if not entries or len(entries) > MAX_ENTRIES:
            raise ValueError("unexpected ZIP entry count")
        seen: set[str] = set()
        total = 0
        for info in entries:
            raw = info.filename
            member = PurePosixPath(raw)
            parts = member.parts
            if (
                not raw or "\\" in raw or raw.startswith("/")
                or not parts or any(part in {"..", "."} for part in parts)
                or re.match(r"^[A-Za-z]:", raw)
            ):
                raise ValueError(f"unsafe ZIP member: {raw!r}")
            if raw in seen:
                raise ValueError(f"duplicate ZIP member: {raw!r}")
            seen.add(raw)
            if any(part in FORBIDDEN_PARTS for part in parts):
                raise ValueError(f"excluded directory in ZIP: {raw!r}")
            if (
                member.name in FORBIDDEN_FILES
                or (member.name.startswith(".env.") and member.name not in ALLOWED_TEMPLATES)
                or (member.name.startswith("secrets.toml.") and member.name not in ALLOWED_TEMPLATES)
                or member.name.endswith(FORBIDDEN_SUFFIXES)
            ):
                raise ValueError(f"private/generated file in ZIP: {raw!r}")
            if stat.S_IFMT(info.external_attr >> 16) == stat.S_IFLNK:
                raise ValueError(f"symbolic link in ZIP: {raw!r}")
            total += info.file_size
            if total > MAX_TOTAL_SIZE:
                raise ValueError("ZIP expands beyond safe review limit")
        if archive.testzip() is not None:
            raise ValueError("ZIP CRC failure")
    print(f"{path.name}: PASS ({len(entries)} entries, SHA-256 {digest})")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, help="Original v2 ZIP or reviewed MatCount RC1 ZIP")
    parser.add_argument("--manifest", type=Path, help="External .sha256 for a clean extracted copy")
    args = parser.parse_args()
    try:
        check_manifests()
        check_source()
        print("Committed checksum and repository source exclusions: PASS")
        if args.archive:
            check_archive(args.archive, args.manifest)
        else:
            print("Original archive bytes: NOT CHECKED (pass --archive to verify)")
        return 0
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"Release integrity: FAIL ({exc})", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
