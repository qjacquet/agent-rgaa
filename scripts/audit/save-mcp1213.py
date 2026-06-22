#!/usr/bin/env python3
"""Save MCP browser_cdp JSON response and process themes 12-13."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PROCESS = ROOT / "scripts" / "audit" / "process-theme1213.py"


def main() -> None:
    if len(sys.argv) < 5:
        print("Usage: save-mcp1213.py <audit_dir> <sample> <url> <mcp_cdp.json>", file=sys.stderr)
        sys.exit(1)
    subprocess.run([sys.executable, str(PROCESS), *sys.argv[1:5]], check=True)


if __name__ == "__main__":
    main()
