#!/usr/bin/env python3
"""Save inline CDP value dict and log themes 5-8 for a sample."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def main() -> None:
    if len(sys.argv) < 5:
        print("Usage: save-theme5678-value.py <audit_dir> <sample> <url> <value.json>", file=sys.stderr)
        sys.exit(1)
    audit_dir, sample, url, val_path = sys.argv[1:5]
    audit = Path(audit_dir)
    data = json.loads(Path(val_path).read_text(encoding="utf-8"))
    out = audit / "evidence" / f"{sample}-theme5678-combined.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    run = ROOT / "scripts" / "audit" / "run-theme5678-sample.py"
    subprocess.run([sys.executable, str(run), str(audit), sample, url, str(out)], check=True)
    print(f"saved+logged {sample}")


if __name__ == "__main__":
    main()
