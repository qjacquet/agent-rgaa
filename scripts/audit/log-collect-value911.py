#!/usr/bin/env python3
"""Log theme 9-11 from a collect value JSON file (theme9/10/11 keys)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RUN = ROOT / "scripts" / "audit" / "run-theme911-only.py"


def main() -> None:
    if len(sys.argv) < 5:
        print("Usage: log-collect-value911.py <audit_dir> <sample> <url> <value.json>", file=sys.stderr)
        sys.exit(1)
    audit_dir, sample, url, src = sys.argv[1:5]
    val = json.loads(Path(src).read_text(encoding="utf-8"))
    out = Path(f"/tmp/mcp911-{sample}.json")
    out.write_text(json.dumps({"result": {"value": val}}, ensure_ascii=False), encoding="utf-8")
    subprocess.run([sys.executable, str(RUN), audit_dir, sample, url, str(out)], check=True)


if __name__ == "__main__":
    main()
