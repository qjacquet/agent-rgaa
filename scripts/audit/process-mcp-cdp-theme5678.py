#!/usr/bin/env python3
"""Process MCP CDP result file -> save value -> log themes 5-8."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SAVE = ROOT / "scripts" / "audit" / "save-theme5678-value.py"


def extract(raw: dict) -> dict:
    if "exceptionDetails" in raw:
        raise SystemExit(f"CDP error: {raw['exceptionDetails']}")
    r = raw.get("result", raw)
    if isinstance(r, dict) and "value" in r:
        return r["value"]
    if "value" in raw:
        return raw["value"]
    raise SystemExit(f"No value in {list(raw.keys())}")


def main() -> None:
    if len(sys.argv) < 5:
        print("Usage: process-mcp-cdp-theme5678.py <audit_dir> <sample> <url> <mcp_cdp.json>", file=sys.stderr)
        sys.exit(1)
    audit_dir, sample, url, mcp_path = sys.argv[1:5]
    raw = json.loads(Path(mcp_path).read_text(encoding="utf-8"))
    val_path = Path(f"/tmp/val-{sample}.json")
    val_path.write_text(json.dumps(extract(raw), ensure_ascii=False), encoding="utf-8")
    subprocess.run([sys.executable, str(SAVE), audit_dir, sample, url, str(val_path)], check=True)


if __name__ == "__main__":
    main()
