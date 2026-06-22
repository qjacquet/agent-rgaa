#!/usr/bin/env python3
"""Save MCP CDP result JSON from file and log theme234."""
import json, subprocess, sys
from pathlib import Path

AUDIT, sample, url, src = Path(sys.argv[1]), sys.argv[2], sys.argv[3], Path(sys.argv[4])
raw = json.loads(src.read_text())
val = raw.get('result', raw)
if isinstance(val, dict) and 'value' in val:
    val = val['value']
out = Path('/tmp/collected') / f'{sample}.json'
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps({'result': {'value': val}}, ensure_ascii=False))
subprocess.run([
    sys.executable,
    str(Path(__file__).resolve().parent / 'log-compact-collect.py'),
    str(AUDIT), sample, url, str(out),
], check=True)
