"""Build a deterministic source-only RC2 bundle and independently verify it."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import subprocess
import zipfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
NAME = "MatCount_SEMS_v2_Offline_Faculty_Demo_FINAL_v2.0.0-rc.2"
FORBIDDEN = {".git", ".venv", "venv", "node_modules", ".next", "__pycache__", ".pytest_cache", "coverage", "logs", ".env", ".env.local", "secrets.toml"}


def source_entries(commit: str, supplied_tree: Path | None) -> dict[str, str]:
    if supplied_tree:
        data = json.loads(supplied_tree.read_text(encoding="utf-8"))
        if data.get("truncated"):
            raise ValueError("Incomplete Git tree")
        return {entry["path"]: entry["sha"] for entry in data["tree"] if entry["type"] == "blob"}
    result = subprocess.check_output(["git", "ls-tree", "-r", "-z", commit], cwd=ROOT)
    entries = {}
    for record in result.split(b"\0"):
        if not record:
            continue
        metadata, path = record.split(b"\t", 1)
        mode, kind, sha = metadata.decode().split()
        if kind != "blob" or mode not in {"100644", "100755"}:
            raise ValueError("Unsupported source object")
        entries[path.decode("utf-8")] = sha
    return entries


def safe_path(name: str) -> None:
    path = PurePosixPath(name)
    if not name or name.startswith("/") or "\\" in name or any(part in {"..", "."} | FORBIDDEN for part in path.parts) or re.match(r"^[A-Za-z]:", name):
        raise ValueError(f"Excluded source path: {name}")
    if path.suffix.lower() in {".zip", ".sqlite", ".sqlite3", ".db", ".bak", ".log", ".pyc"}:
        raise ValueError(f"Excluded source file: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--tree", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[a-f0-9]{40}", args.commit):
        raise ValueError("Require an exact immutable commit SHA")
    entries = source_entries(args.commit, args.tree)
    if not args.tree:
        # Checkout filters intentionally make PowerShell files CRLF. Export raw
        # Git blobs so archive bytes still match the selected immutable tree.
        subprocess.check_call(["git", "diff", "--quiet", args.commit, "--"], cwd=ROOT)
    if "SOURCE_COMMIT.txt" in entries:
        raise ValueError("Distribution metadata must not replace a committed source file")
    payload = {}
    for name, expected in sorted(entries.items()):
        safe_path(name)
        path = ROOT / name
        if path.is_symlink():
            raise ValueError("Symlinks are excluded")
        content = path.read_bytes() if args.tree else subprocess.check_output(
            ["git", "cat-file", "blob", expected], cwd=ROOT
        )
        actual = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
        if actual != expected:
            raise ValueError(f"Source differs from selected commit: {name}")
        payload[f"{NAME}/{name}"] = content
    payload[f"{NAME}/SOURCE_COMMIT.txt"] = (f"{args.commit}\nv2.0.0-rc.2\nAcademic release candidate; intended-host acceptance pending.\n").encode()
    args.out.mkdir(parents=True, exist_ok=True)
    archive = args.out / f"{NAME}.zip"
    if archive.exists():
        raise ValueError("Refusing to overwrite existing candidate bytes")
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as output:
        for name, content in sorted(payload.items()):
            info = zipfile.ZipInfo(name, date_time=(2000, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            output.writestr(info, content, compresslevel=9)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (args.out / f"{NAME}.zip.sha256").write_text(f"{digest}  {archive.name}\n", encoding="ascii")
    manifest = args.out / f"{NAME}_FILE_MANIFEST_SHA256.txt"
    manifest.write_text("".join(f"{hashlib.sha256(content).hexdigest()}  {name}\n" for name, content in sorted(payload.items())), encoding="utf-8")
    clean = args.out / "Clean Extraction With Spaces"
    if clean.exists():
        raise ValueError("Clean extraction directory already exists")
    with zipfile.ZipFile(archive) as source:
        if source.testzip() or len(source.namelist()) != len(payload):
            raise ValueError("Archive verification failed")
        for member in source.infolist():
            safe_path(member.filename)
            if source.read(member) != payload[member.filename]:
                raise ValueError("Archive entry bytes changed")
        source.extractall(clean)
    for line in manifest.read_text(encoding="utf-8").splitlines():
        expected, name = line.split("  ", 1)
        if hashlib.sha256((clean / name).read_bytes()).hexdigest() != expected:
            raise ValueError("Extracted manifest mismatch")
    result = {"commit": args.commit, "tag": "v2.0.0-rc.2", "archive": archive.name, "sha256": digest, "size_bytes": archive.stat().st_size, "entries": len(payload), "git_files": len(entries), "distribution_metadata": ["SOURCE_COMMIT.txt"], "clean_root": str((clean / NAME).resolve())}
    (args.out / "package-result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
