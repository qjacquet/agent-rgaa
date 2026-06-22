#!/usr/bin/env python3
"""Save MCP browser_cdp Runtime.evaluate result and log themes 5-8."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def extract_value(raw: dict) -> dict:
    if raw.get("type") == "metadata":
        raw = {k: v for k, v in raw.items() if k != "type"}
    if "result" in raw:
        r = raw["result"]
        if isinstance(r, dict):
            if "value" in r:
                return r["value"]
            if "result" in r and isinstance(r["result"], dict) and "value" in r["result"]:
                return r["result"]["value"]
    if "value" in raw:
        return raw["value"]
    raise SystemExit(f"No CDP value in response keys={list(raw.keys())}")


def main() -> None:
    if len(sys.argv) < 5:
        print("Usage: save-mcp-cdp-theme5678.py <audit_dir> <sample> <url> <mcp_response.json>", file=sys.stderr)
        sys.exit(1)
    audit_dir, sample, url, resp_path = sys.argv[1:5]
    raw = json.loads(Path(resp_path).read_text(encoding="utf-8"))
    if "exceptionDetails" in raw:
        raise SystemExit(f"CDP exception: {raw.get('exceptionDetails', raw)}")
    data = extract_value(raw)
    out = Path(audit_dir) / "evidence" / f"{sample}-theme5678-combined.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    run = ROOT / "scripts" / "audit" / "run-theme5678-sample.py"
    subprocess.run([sys.executable, str(run), audit_dir, sample, url, str(out)], check=True)
    print(f"saved+logged {sample}")


if __name__ == "__main__":
    main()
