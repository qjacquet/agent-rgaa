#!/usr/bin/env python3
"""Print theme911-only CDP expression."""
from pathlib import Path
print((Path(__file__).resolve().parent / "theme911-only-collect.js").read_text(encoding="utf-8"), end="")
