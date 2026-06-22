#!/usr/bin/env python3
"""Log all theme234 collects from /tmp/collected/{sample}.json files."""
import json, subprocess, sys
from pathlib import Path

AUDIT = Path(sys.argv[1])
COLLECTED = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('/tmp/collected')
SCRIPTS = Path(__file__).resolve().parent
SAMPLES = json.loads((AUDIT / 'samples-status.json').read_text())['samples']

for s in SAMPLES:
    slug, url = s['slug'], s['url']
    p = COLLECTED / f'{slug}.json'
    if not p.exists():
        continue
    subprocess.run([
        sys.executable, str(SCRIPTS / 'log-compact-collect.py'),
        str(AUDIT), slug, url, str(p),
    ], check=True)
    print('logged', slug)
