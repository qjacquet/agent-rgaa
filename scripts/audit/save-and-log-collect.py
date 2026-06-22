#!/usr/bin/env python3
"""Save MCP CDP collect value and log theme234."""
import json, subprocess, sys
from pathlib import Path

AUDIT = Path(sys.argv[1])
sample, url, src = sys.argv[2], sys.argv[3], Path(sys.argv[4])
SCRIPTS = Path(__file__).resolve().parent
raw = json.loads(src.read_text())
val = raw.get('result', {}).get('value', raw)
if 'type' in val and 'value' in val:
    val = val['value']
out = AUDIT / 'evidence' / f'{sample}-collect-raw.json'
out.write_text(json.dumps(val, ensure_ascii=False, indent=2))
wrapped = AUDIT / 'evidence' / f'{sample}-mcp-wrap.json'
wrapped.write_text(json.dumps({'result': {'value': val}}, ensure_ascii=False))
subprocess.run([sys.executable, str(SCRIPTS / 'log-compact-collect.py'), str(AUDIT), sample, url, str(wrapped)], check=True)
