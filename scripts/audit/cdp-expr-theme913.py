#!/usr/bin/env python3
"""Print theme913 merged CDP expression for browser_cdp Runtime.evaluate."""
from pathlib import Path
import sys

path = Path(__file__).resolve().parent / "theme913-merged-collect.js"
print(path.read_text(encoding="utf-8"), end="")
