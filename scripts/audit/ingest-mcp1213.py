#!/usr/bin/env python3
"""Ingest MCP browser_cdp JSON response and log themes 12-13 for one sample."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PROCESS = ROOT / "scripts" / "audit" / "process-theme1213.py"


def extract(raw: dict) -> dict:
    if "exceptionDetails" in raw:
        raise SystemExit(f"CDP error: {raw['exceptionDetails']}")
    r = raw.get("result", raw)
    if isinstance(r, dict) and "value" in r:
        return r["value"]
    if "value" in raw:
        return raw["value"]
    if "theme12" in raw or "theme13" in raw:
        return raw
    raise SystemExit(f"No value in {list(raw.keys())}")


def main() -> None:
    if len(sys.argv) < 5:
        print("Usage: ingest-mcp1213.py <audit_dir> <sample> <url> <mcp_json_file>", file=sys.stderr)
        sys.exit(1)
    audit_dir, sample, url, src = sys.argv[1:5]
    raw = json.loads(Path(src).read_text(encoding="utf-8"))
    out = Path(f"/tmp/mcp1213-{sample}.json")
    out.write_text(json.dumps({"result": {"value": extract(raw)}}, ensure_ascii=False), encoding="utf-8")
    subprocess.run([sys.executable, str(PROCESS), audit_dir, sample, url, str(out)], check=True)


if __name__ == "__main__":
    main()
