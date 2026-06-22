#!/usr/bin/env python3
"""Split theme913-combined-collect.js into per-theme CDP expressions."""
from __future__ import annotations

import base64
import json
import re
from pathlib import Path

SRC = Path(__file__).resolve().parent / "theme913-combined-collect.js"
text = SRC.read_text(encoding="utf-8")

# Extract helper preamble (lines before theme9 comment)
preamble_end = text.index("// --- Theme 9:")
preamble = text[:preamble_end]

themes = {}
for m in re.finditer(r"// --- Theme (\d+): ([^\n]+)\n", text):
    tid = m.group(1)
    start = m.end()
    nxt = text.find("// --- Theme ", start)
    body = text[start:nxt if nxt != -1 else text.index("\n  return {")]
    themes[tid] = body

return_block = """
  return {
    url: location.href,
    title: document.title,
"""

for tid in ["9", "10", "11", "12", "13"]:
    chunk = f"(() => {{\n{preamble}{themes[tid]}{return_block}    theme{tid}: theme{tid}Data,\n  }};\n}})()"
    # fix: wrap body in const themeXData = {...}
    body = themes[tid].strip()
    if not body.endswith(";"):
        body += ";"
    # rename - the body uses const headings etc directly; rebuild full script per theme from combined
    pass

print("themes found:", list(themes.keys()))
