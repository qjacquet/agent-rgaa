#!/usr/bin/env python3
"""Build CDP Runtime.evaluate request JSON for theme 12+13 collect."""
import json
import sys
from pathlib import Path

expr = (Path(__file__).resolve().parent / "theme1213-collect.js").read_text(encoding="utf-8")
payload = {
    "method": "Runtime.evaluate",
    "params": {"expression": expr, "returnByValue": True},
}
print(json.dumps(payload))
