#!/usr/bin/env python3
"""Save CDP collect JSON and batch-log theme 1 tests for one sample."""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def main() -> None:
    audit_dir = Path(sys.argv[1])
    sample = sys.argv[2]
    url = sys.argv[3]
    data = json.loads(Path(sys.argv[4]).read_text(encoding="utf-8"))
    skip = sys.argv[5] if len(sys.argv) > 5 else ""
    out = audit_dir / "evidence" / f"{sample}-theme1.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    cmd = [
        sys.executable,
        str(ROOT / "scripts/audit/eval-theme1-batch.py"),
        str(audit_dir),
        "--sample",
        sample,
        "--url",
        url,
        "--collect",
        str(out),
    ]
    if skip:
        cmd.extend(["--skip", skip])
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
