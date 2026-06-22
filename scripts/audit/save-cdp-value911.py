#!/usr/bin/env python3
"""Save CDP collect value JSON and log themes 9-11 for one sample."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LOG = ROOT / "scripts" / "audit" / "log-collect-value911.py"


def main() -> None:
    if len(sys.argv) < 4:
        print("Usage: save-cdp-value911.py <audit_dir> <sample> <url> [value.json|-]", file=sys.stderr)
        sys.exit(1)
    audit_dir, sample, url = sys.argv[1:4]
    src = sys.argv[4] if len(sys.argv) > 4 else "-"
    raw = sys.stdin.read() if src == "-" else Path(src).read_text(encoding="utf-8")
    val = json.loads(raw)
    if "result" in val and isinstance(val["result"], dict) and "value" in val["result"]:
        val = val["result"]["value"]
    ev_dir = Path(audit_dir) / "evidence"
    ev_dir.mkdir(parents=True, exist_ok=True)
    out = ev_dir / f"{sample}-theme911-combined.json"
    out.write_text(json.dumps(val, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    subprocess.run([sys.executable, str(LOG), audit_dir, sample, url, str(out)], check=True)


if __name__ == "__main__":
    main()
