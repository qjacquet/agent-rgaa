#!/usr/bin/env python3
"""Save MCP CDP JSON from argv file and process themes 9-13 for one sample."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PROCESS = ROOT / "scripts" / "audit" / "process-mcp-cdp-theme913.py"


def main() -> None:
    if len(sys.argv) < 5:
        print("Usage: save-mcp913.py <audit_dir> <sample> <url> <mcp_json_file>", file=sys.stderr)
        sys.exit(1)
    audit_dir, sample, url, src = sys.argv[1:5]
    raw = json.loads(Path(src).read_text(encoding="utf-8"))
    out = Path(f"/tmp/mcp913-{sample}.json")
    out.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    subprocess.run([sys.executable, str(PROCESS), audit_dir, sample, url, str(out)], check=True)


if __name__ == "__main__":
    main()
