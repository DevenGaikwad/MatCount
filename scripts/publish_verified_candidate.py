"""Publish only the validated RC2 bytes and verify authenticated downloads."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path


REPOSITORY = "DevenGaikwad/MatCount"


def gh(*args: str) -> str:
    return subprocess.check_output(["gh", *args], text=True)


def ensure_tag(tag: str, commit: str) -> None:
    result = subprocess.run(["gh", "api", f"repos/{REPOSITORY}/git/ref/tags/{tag}"], text=True, capture_output=True, check=False)
    if result.returncode == 0:
        if json.loads(result.stdout)["object"]["sha"] != commit:
            raise ValueError("Existing tag points elsewhere; never move it")
        return
    if "404" not in result.stderr:
        raise RuntimeError("Could not inspect tag; no write attempted")
    gh("api", "--method", "POST", f"repos/{REPOSITORY}/git/refs", "-f", f"ref=refs/tags/{tag}", "-f", f"sha={commit}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()
    directory = args.directory.resolve()
    package = json.loads((directory / "package-result.json").read_text())
    validation = json.loads((directory / "validation-result.json").read_text())
    if os.environ.get("GITHUB_REPOSITORY") != REPOSITORY or os.environ.get("GITHUB_REF") != "refs/heads/release/offline-faculty-rc2" or os.environ.get("GITHUB_SHA") != package["commit"]:
        raise ValueError("Publication requires the authorized exact repository/branch/commit")
    if len(validation["checks"]) != 17 or any(check["exit_code"] for check in validation["checks"]):
        raise ValueError("Candidate validation is incomplete")
    archive = directory / package["archive"]
    if hashlib.sha256(archive.read_bytes()).hexdigest() != package["sha256"]:
        raise ValueError("Archive changed after validation")
    existing = subprocess.run(["gh", "api", f"repos/{REPOSITORY}/releases/tags/v2.0.0-rc.2"], text=True, capture_output=True, check=False)
    if existing.returncode == 0:
        raise ValueError("An RC2 release already exists; no assets will be overwritten")
    if "404" not in existing.stderr:
        raise RuntimeError("Could not inspect prerelease; no write attempted")
    ensure_tag("v2.0.0-rc.1", "147d285eaa8ab4beed274da3b2adedf45648c36b")
    ensure_tag("v2.0.0-rc.2", package["commit"])
    stem = archive.name[:-4]
    assets = [archive, directory / (archive.name + ".sha256"), directory / (stem + "_FILE_MANIFEST_SHA256.txt"), directory / (stem + "_VALIDATION_REPORT.md")]
    gh("release", "create", "v2.0.0-rc.2", *(str(path) for path in assets), "--repo", REPOSITORY, "--verify-tag", "--prerelease", "--latest=false", "--title", "MatCount v2.0.0 RC2 — Windows/MySQL Acceptance Pending", "--notes-file", str(directory / "RELEASE_NOTES.md"))
    downloaded = directory / "Verified Release Downloads"
    downloaded.mkdir()
    gh("release", "download", "v2.0.0-rc.2", "--repo", REPOSITORY, "--dir", str(downloaded))
    evidence = []
    for asset in assets:
        remote = downloaded / asset.name
        expected = hashlib.sha256(asset.read_bytes()).hexdigest()
        actual = hashlib.sha256(remote.read_bytes()).hexdigest()
        if actual != expected or remote.stat().st_size != asset.stat().st_size:
            raise ValueError("Post-upload asset differs; keep repository private and investigate")
        evidence.append({"name": asset.name, "size_bytes": remote.stat().st_size, "sha256": actual})
    release = json.loads(gh("api", f"repos/{REPOSITORY}/releases/tags/v2.0.0-rc.2"))
    if not release["prerelease"] or release["draft"]:
        raise ValueError("Release state is not an active prerelease")
    result = {"release_url": release["html_url"], "release_id": release["id"], "tag": release["tag_name"], "commit": package["commit"], "prerelease": release["prerelease"], "github_immutable_release_flag": release.get("immutable", False), "assets": evidence}
    (directory / "publication-result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
