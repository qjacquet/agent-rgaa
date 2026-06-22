#!/usr/bin/env python3
"""Process CDP collect result from stdin and log themes 5-8 for one sample."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def main() -> None:
    if len(sys.argv) < 4:
        print("Usage: log-theme5678-stdin.py <audit_dir> <sample> <url>", file=sys.stderr)
        sys.exit(1)
    audit_dir, sample, url = sys.argv[1:4]
    raw = json.load(sys.stdin)
    data = raw.get("result", raw)
    if isinstance(data, dict) and "value" in data:
        data = data["value"]
    audit = Path(audit_dir)
    out = audit / "evidence" / f"{sample}-theme5678-combined.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    run = ROOT / "scripts" / "audit" / "run-theme5678-sample.py"
    subprocess.run([sys.executable, str(run), str(audit_dir), sample, url, str(out)], check=True)


if __name__ == "__main__":
    main()
