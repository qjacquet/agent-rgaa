#!/usr/bin/env python3
"""Orchestrate theme 5-8 audit: process saved CDP collect JSON for all samples."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
AUDIT = ROOT / "audits" / "cmvmediforce" / "2026-06-22"
SAMPLES = json.loads((AUDIT / "samples-status.json").read_text())["samples"]
RUN = ROOT / "scripts" / "audit" / "run-theme5678-sample.py"


def process(sample: str, url: str, collect_path: Path) -> None:
    if not collect_path.exists():
        print(f"MISSING {collect_path}", file=sys.stderr)
        return
    subprocess.run([sys.executable, str(RUN), str(AUDIT), sample, url, str(collect_path)], check=True)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: batch-process-theme5678.py all|<sample>", file=sys.stderr)
        sys.exit(1)
    target = sys.argv[1]
    for s in SAMPLES:
        if target != "all" and s["slug"] != target:
            continue
        path = AUDIT / "evidence" / f"{s['slug']}-theme5678-combined.json"
        process(s["slug"], s["url"], path)


if __name__ == "__main__":
    main()
