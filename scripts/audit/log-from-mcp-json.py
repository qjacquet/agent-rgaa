#!/usr/bin/env python3
"""Log theme234 from MCP CDP result JSON file (result.value or theme2/3/4)."""
import json, subprocess, sys
from pathlib import Path

AUDIT = Path(sys.argv[1])
sample, url, src = sys.argv[2], sys.argv[3], Path(sys.argv[4])
raw = json.loads(src.read_text())
val = raw.get('result', raw)
if isinstance(val, dict) and 'value' in val:
    val = val['value']
if 'theme2' not in val:
    val = raw  # flat already
wrap = Path(f'/tmp/{sample}-wrap.json')
wrap.write_text(json.dumps({'result': {'value': val}}, ensure_ascii=False))
subprocess.run([
    sys.executable,
    str(Path(__file__).resolve().parent / 'log-compact-collect.py'),
    str(AUDIT), sample, url, str(wrap),
], check=True)
print(f'logged {sample}')
