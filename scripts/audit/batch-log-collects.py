#!/usr/bin/env python3
"""Batch log theme234 from list of {sample, url, result} objects."""
import json, subprocess, sys
from pathlib import Path

AUDIT = Path(sys.argv[1])
items = json.loads(Path(sys.argv[2]).read_text())
SCRIPTS = Path(__file__).resolve().parent
for item in items:
    val = item['result'].get('result', {}).get('value', item['result'])
    for theme, data in [('2', val['theme2']), ('3', val['theme3']), ('4', val['theme4'])]:
        ev = AUDIT / 'evidence' / f"{item['sample']}-theme{theme}.json"
        ev.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        subprocess.run([sys.executable, str(SCRIPTS/f'eval-theme{theme}-batch.py'), str(AUDIT),
            '--sample', item['sample'], '--url', item['url'], '--collect', str(ev)], check=True)
    print('logged', item['sample'])
