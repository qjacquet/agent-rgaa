#!/usr/bin/env python3
"""Log theme234 from compact MCP collect value dict."""
import json, subprocess, sys
from pathlib import Path

AUDIT = Path(sys.argv[1])
sample, url, src = sys.argv[2], sys.argv[3], Path(sys.argv[4])
SCRIPTS = Path(__file__).resolve().parent
raw = json.loads(src.read_text())
val = raw.get('result', {}).get('value', raw)
for theme, data in [('2', val['theme2']), ('3', val['theme3']), ('4', val['theme4'])]:
    ev = AUDIT / 'evidence' / f'{sample}-theme{theme}.json'
    ev.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    subprocess.run([sys.executable, str(SCRIPTS/f'eval-theme{theme}-batch.py'), str(AUDIT), '--sample', sample, '--url', url, '--collect', str(ev)], check=True)
print('logged', sample)
