#!/usr/bin/env python3
"""Print theme5678 compact CDP expression for browser_cdp Runtime.evaluate."""
from pathlib import Path

EXPR = (Path(__file__).resolve().parent / "theme5678-compact-collect.js").read_text(encoding="utf-8")

if __name__ == "__main__":
    print(EXPR)
