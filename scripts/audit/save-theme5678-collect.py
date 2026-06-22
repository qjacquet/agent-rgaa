#!/usr/bin/env python3
"""Save MCP CDP collect result and log themes 5-8 for one sample."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def main() -> None:
    if len(sys.argv) < 5:
        print("Usage: save-theme5678-collect.py <audit_dir> <sample> <url> <mcp_result_json>", file=sys.stderr)
        sys.exit(1)
    audit_dir = Path(sys.argv[1])
    sample, url, result_path = sys.argv[2], sys.argv[3], Path(sys.argv[4])
    raw = json.loads(result_path.read_text(encoding="utf-8"))
    data = raw.get("result", raw)
    if isinstance(data, dict) and "value" in data:
        data = data["value"]
    out = audit_dir / "evidence" / f"{sample}-theme5678-combined.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    run = ROOT / "scripts" / "audit" / "run-theme5678-sample.py"
    subprocess.run([sys.executable, str(run), str(audit_dir), sample, url, str(out)], check=True)
    print(f"saved+logged {sample} -> {out}")


if __name__ == "__main__":
    main()
