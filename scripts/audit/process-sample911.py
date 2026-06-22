#!/usr/bin/env python3
"""Process one sample's merged theme911 CDP MCP response and log themes 9-11."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RUN = ROOT / "scripts" / "audit" / "run-theme911-only.py"


def extract(raw: dict) -> dict:
    if "exceptionDetails" in raw:
        raise SystemExit(f"CDP error: {raw['exceptionDetails']}")
    r = raw.get("result", raw)
    if isinstance(r, dict) and "value" in r:
        return r["value"]
    if "value" in raw:
        return raw["value"]
    return raw


def main() -> None:
    if len(sys.argv) < 5:
        print("Usage: process-sample911.py <audit_dir> <sample> <url> <mcp_cdp.json>", file=sys.stderr)
        sys.exit(1)
    audit_dir, sample, url, src = sys.argv[1:5]
    raw = json.loads(Path(src).read_text(encoding="utf-8"))
    out = Path(f"/tmp/mcp911-{sample}.json")
    out.write_text(json.dumps({"result": {"value": extract(raw)}}, ensure_ascii=False), encoding="utf-8")
    subprocess.run([sys.executable, str(RUN), audit_dir, sample, url, str(out)], check=True)
    print(f"done {sample}")


if __name__ == "__main__":
    main()
