#!/usr/bin/env python3
"""Batch log themes 9-11 from JSONL: one object per line {sample, url, value}."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LOG = ROOT / "scripts" / "audit" / "log-collect-value911.py"


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: batch-log-theme911-collects.py <audit_dir> <collects.jsonl>", file=sys.stderr)
        sys.exit(1)
    audit_dir = Path(sys.argv[1])
    src = Path(sys.argv[2])
    done = 0
    for line in src.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        tmp = Path(f"/tmp/collect911-{item['sample']}.json")
        tmp.write_text(json.dumps(item["value"], ensure_ascii=False), encoding="utf-8")
        subprocess.run(
            [sys.executable, str(LOG), str(audit_dir), item["sample"], item["url"], str(tmp)],
            check=True,
        )
        done += 1
        print(f"logged {item['sample']}")
    print(f"batch done: {done} samples")


if __name__ == "__main__":
    main()
