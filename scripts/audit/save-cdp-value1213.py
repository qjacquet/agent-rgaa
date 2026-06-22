#!/usr/bin/env python3
"""Save CDP collect value (raw or MCP-wrapped) and log themes 12-13."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PROCESS = ROOT / "scripts" / "audit" / "process-theme1213.py"


def wrap_value(data: dict) -> dict:
    if "theme12" in data or "theme13" in data:
        return {"result": {"value": data}}
    return data


def main() -> None:
    if len(sys.argv) < 5:
        print("Usage: save-cdp-value1213.py <audit_dir> <sample> <url> <json_file>", file=sys.stderr)
        sys.exit(1)
    audit_dir, sample, url, infile = sys.argv[1], sys.argv[2], sys.argv[3], Path(sys.argv[4])
    raw = json.loads(infile.read_text(encoding="utf-8"))
    wrapped = wrap_value(raw)
    tmp = Path(f"/tmp/mcp1213-{sample}.json")
    tmp.write_text(json.dumps(wrapped, ensure_ascii=False), encoding="utf-8")
    subprocess.run([sys.executable, str(PROCESS), audit_dir, sample, url, str(tmp)], check=True)


if __name__ == "__main__":
    main()
