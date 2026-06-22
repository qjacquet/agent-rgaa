#!/usr/bin/env python3
"""Read CDP value JSON from stdin, save evidence and log themes 5-8."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SAVE = ROOT / "scripts" / "audit" / "save-theme5678-value.py"


def main() -> None:
    if len(sys.argv) != 4:
        print("Usage: save-theme5678-stdin.py <audit_dir> <sample> <url>", file=sys.stderr)
        sys.exit(1)
    audit_dir, sample, url = sys.argv[1:4]
    data = json.load(sys.stdin)
    val_path = Path(f"/tmp/val-{sample}.json")
    val_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    subprocess.run([sys.executable, str(SAVE), audit_dir, sample, url, str(val_path)], check=True)


if __name__ == "__main__":
    main()
