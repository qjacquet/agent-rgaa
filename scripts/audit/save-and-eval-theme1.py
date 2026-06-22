#!/usr/bin/env python3
"""Save MCP CDP collect result and batch-log theme 1 tests."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
EVAL = ROOT / "scripts" / "audit" / "eval-theme1-batch.py"


def main() -> None:
    audit_dir = Path(sys.argv[1])
    sample = sys.argv[2]
    url = sys.argv[3]
    collect_path = audit_dir / "evidence" / f"{sample}-theme1.json"
    skip = sys.argv[4] if len(sys.argv) > 4 else ""
    data = json.loads(sys.stdin.read())
    collect_path.parent.mkdir(parents=True, exist_ok=True)
    collect_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    cmd = [sys.executable, str(EVAL), str(audit_dir), "--sample", sample, "--url", url, "--collect", str(collect_path)]
    if skip:
        cmd.extend(["--skip", skip])
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
