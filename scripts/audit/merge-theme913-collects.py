#!/usr/bin/env python3
"""Merge per-theme CDP JSON files and log themes 9-13 for one sample."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RUN = ROOT / "scripts" / "audit" / "run-theme913-sample.py"


def merge(paths: list[Path]) -> dict:
    out: dict = {}
    for p in paths:
        raw = json.loads(p.read_text(encoding="utf-8"))
        if "result" in raw and "value" in raw.get("result", {}):
            val = raw["result"]["value"]
        elif "value" in raw:
            val = raw["value"]
        else:
            val = raw
        out.update(val)
    return out


def main() -> None:
    if len(sys.argv) < 4:
        print("Usage: merge-theme913-collects.py <audit_dir> <sample> <url> <t9.json> <t10.json> ...", file=sys.stderr)
        sys.exit(1)
    audit_dir, sample, url = sys.argv[1], sys.argv[2], sys.argv[3]
    paths = [Path(p) for p in sys.argv[4:]]
    merged = merge(paths)
    out = Path(f"/tmp/val913-{sample}.json")
    out.write_text(json.dumps(merged, ensure_ascii=False), encoding="utf-8")
    subprocess.run([sys.executable, str(RUN), audit_dir, sample, url, str(out)], check=True)


if __name__ == "__main__":
    main()
