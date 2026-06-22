#!/usr/bin/env python3
"""Process all /tmp/mcp1213-*.json files for themes 12-13."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
AUDIT = ROOT / "audits" / "cmvmediforce" / "2026-06-22"
PROCESS = ROOT / "scripts" / "audit" / "process-theme1213.py"
SAMPLES = {s["slug"]: s["url"] for s in json.loads((AUDIT / "samples-status.json").read_text())["samples"]}


def main() -> None:
    audit_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else AUDIT
    done = 0
    for path in sorted(Path("/tmp").glob("mcp1213-*.json")):
        sample = path.stem.replace("mcp1213-", "")
        url = SAMPLES.get(sample, "")
        if not url:
            print(f"SKIP unknown sample {sample}", file=sys.stderr)
            continue
        subprocess.run([sys.executable, str(PROCESS), str(audit_dir), sample, url, str(path)], check=True)
        done += 1
        print(f"processed {sample}")
    print(f"batch replay: {done} samples")


if __name__ == "__main__":
    main()
