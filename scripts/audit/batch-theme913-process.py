#!/usr/bin/env python3
"""Run theme 9-13 CDP collect via Playwright CDP if WS URL provided, else process saved MCP JSON."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
AUDIT = ROOT / "audits" / "cmvmediforce" / "2026-06-22"
EXPR = Path(__file__).resolve().parent / "theme913-combined-collect.js"
PROCESS = ROOT / "scripts" / "audit" / "process-mcp-cdp-theme913.py"
SAMPLES = json.loads((AUDIT / "samples-status.json").read_text())["samples"]


def process_file(sample: str, url: str, mcp_path: Path) -> None:
    subprocess.run([sys.executable, str(PROCESS), str(AUDIT), sample, url, str(mcp_path)], check=True)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: batch-theme913-process.py all|<sample>", file=sys.stderr)
        sys.exit(1)
    target = sys.argv[1]
    for s in SAMPLES:
        if target != "all" and s["slug"] != target:
            continue
        path = Path(f"/tmp/mcp913-{s['slug']}.json")
        if not path.exists():
            print(f"MISSING {path}", file=sys.stderr)
            continue
        process_file(s["slug"], s["url"], path)
        print(f"processed {s['slug']}")


if __name__ == "__main__":
    main()
