"""Verify actual localhost entry points without claiming live MySQL acceptance."""

from __future__ import annotations

import json
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]


def response(url: str, process: subprocess.Popen) -> bytes:
    for _ in range(100):
        if process.poll() is not None:
            raise RuntimeError("Local service exited before readiness")
        try:
            with urlopen(url, timeout=2) as result:
                if result.status == 200:
                    return result.read()
        except OSError:
            time.sleep(0.2)
    raise RuntimeError("Local service readiness timed out")


def main() -> int:
    for port in (8000, 3000):
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", port))
    processes = []
    try:
        api = subprocess.Popen([sys.executable, "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", "8000"], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        processes.append(api)
        health = json.loads(response("http://127.0.0.1:8000/api/health", api))
        web = subprocess.Popen([shutil.which("node") or "node", str(ROOT / "frontend/node_modules/next/dist/bin/next"), "start", "--hostname", "127.0.0.1", "--port", "3000"], cwd=ROOT / "frontend", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        processes.append(web)
        html = response("http://127.0.0.1:3000/login", web)
        if b"<html" not in html.lower():
            raise RuntimeError("Frontend did not return HTML")
        print("Local services: PASS; API health and production login HTTP 200; live database acceptance not established")
        # Do not print the health payload, which can include environment details.
        if not isinstance(health, dict):
            raise RuntimeError("Unexpected API health envelope")
        return 0
    finally:
        for process in reversed(processes):
            process.terminate()
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
