#!/usr/bin/env python3
"""Store base64-encoded MCP CDP response and ingest themes 12-13."""
from __future__ import annotations

import base64
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
INGEST = ROOT / "scripts" / "audit" / "ingest-mcp1213.py"


def main() -> None:
    if len(sys.argv) < 5:
        print("Usage: store-mcp1213-b64.py <audit_dir> <sample> <url> <base64>", file=sys.stderr)
        sys.exit(1)
    audit_dir, sample, url, b64 = sys.argv[1:5]
    raw = json.loads(base64.b64decode(b64))
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False)
        tmp = f.name
    subprocess.run([sys.executable, str(INGEST), audit_dir, sample, url, tmp], check=True)


if __name__ == "__main__":
    main()
