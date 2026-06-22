#!/usr/bin/env python3
"""Save CDP MCP JSON response to file."""
import sys
from pathlib import Path
Path(sys.argv[1]).write_text(sys.stdin.read(), encoding="utf-8")
print(f"saved {sys.argv[1]}")
