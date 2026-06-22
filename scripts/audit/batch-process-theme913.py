#!/usr/bin/env python3
"""Process saved merged CDP collect for all samples (expects /tmp/mcp913-{slug}.json)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
AUDIT = ROOT / "audits" / "cmvmediforce" / "2026-06-22"
SAVE = ROOT / "scripts" / "audit" / "save-mcp913.py"
SAMPLES = json.loads((AUDIT / "samples-status.json").read_text())["samples"]


def main() -> None:
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    done = 0
    missing = []
    for s in SAMPLES:
        if target != "all" and s["slug"] != target:
            continue
        path = Path(f"/tmp/mcp913-{s['slug']}.json")
        if not path.exists():
            missing.append(s["slug"])
            continue
        subprocess.run(
            [sys.executable, str(SAVE), str(AUDIT), s["slug"], s["url"], str(path)],
            check=True,
        )
        done += 1
        print(f"logged {s['slug']}")
    if missing:
        print("missing:", ", ".join(missing), file=sys.stderr)
    print(f"processed {done} samples")


if __name__ == "__main__":
    main()
