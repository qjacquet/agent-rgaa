#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path
AUDIT, sample, url, val_path = Path(sys.argv[1]), sys.argv[2], sys.argv[3], Path(sys.argv[4])
val = json.loads(val_path.read_text())
if 'theme2' not in val and 'result' in val:
    val = val['result'].get('value', val)
wrap = Path(f'/tmp/{sample}-wrap.json')
wrap.write_text(json.dumps({'result': {'value': val}}, ensure_ascii=False))
subprocess.run([sys.executable, str(Path(__file__).resolve().parent/'log-compact-collect.py'), str(AUDIT), sample, url, str(wrap)], check=True)
