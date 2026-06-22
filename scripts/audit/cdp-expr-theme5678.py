#!/usr/bin/env python3
"""Print theme5678-collect.js expression for browser_cdp Runtime.evaluate."""
from pathlib import Path
import sys

path = Path(__file__).resolve().parent / "theme5678-collect.js"
if len(sys.argv) > 1 and sys.argv[1] == "--compact":
    path = path.with_name("theme5678-compact-collect.js")
print(path.read_text(encoding="utf-8"), end="")
