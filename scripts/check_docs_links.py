"""Check file-target links in committed Markdown without accessing the network."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"!?(?:\[[^\]]*\])\(([^)]+)\)")
SKIP_DIRS = {".git", ".venv", "node_modules", ".next", "__pycache__", ".pytest_cache"}


def main() -> int:
    failures: list[str] = []
    checked = 0
    for markdown in ROOT.rglob("*.md"):
        if any(part in SKIP_DIRS for part in markdown.relative_to(ROOT).parts):
            continue
        for raw in LINK.findall(markdown.read_text(encoding="utf-8")):
            target = raw.strip().split(" ", 1)[0].strip("<>")
            if target.startswith(("#", "mailto:")) or urlsplit(target).scheme:
                continue
            path = unquote(target.split("#", 1)[0].split("?", 1)[0])
            if not path:
                continue
            checked += 1
            candidate = (markdown.parent / path).resolve()
            if not candidate.is_relative_to(ROOT) or not candidate.exists():
                failures.append(f"{markdown.relative_to(ROOT)}: missing or external local target {path}")
    if failures:
        print("Documentation links: FAIL")
        for item in failures:
            print(f"- {item}")
        return 1
    print(f"Documentation local file links: PASS ({checked} targets)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
