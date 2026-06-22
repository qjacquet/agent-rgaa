#!/usr/bin/env python3
"""Process theme1 CDP JSON file -> log all 59 tests for one sample."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
EVAL = ROOT / "scripts/audit/eval-theme1-batch.py"

def main():
    audit_dir, sample, url, collect_file = sys.argv[1:5]
    skip = sys.argv[5] if len(sys.argv) > 5 else ""
    cmd = [sys.executable, str(EVAL), audit_dir, "--sample", sample, "--url", url, "--collect", collect_file]
    if skip: cmd.extend(["--skip", skip])
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    main()
