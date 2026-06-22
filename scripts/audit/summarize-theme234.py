#!/usr/bin/env python3
"""Generate theme 2/3/4 summary from audit-log.jsonl."""
import json, sys
from collections import defaultdict
from pathlib import Path

AUDIT = Path(sys.argv[1])
fails = defaultdict(list)
counts = {t: defaultdict(int) for t in ('2', '3', '4')}

for line in (AUDIT / 'audit-log.jsonl').read_text().splitlines():
    e = json.loads(line)
    if e.get('event') != 'test_result':
        continue
    t = e.get('theme_id')
    if t not in counts:
        continue
    r = e.get('agent_result')
    counts[t][r] += 1
    if r == 'fail':
        ev = AUDIT / 'evidence' / f"{e['sample']}-theme{t}.json"
        fails[t].append({
            'test': e['test'],
            'sample': e['sample'],
            'evidence': str(ev.relative_to(AUDIT.parent.parent)) if ev.exists() else None,
            'detail': (e.get('evidence') or '')[:120],
        })

print('=== RGAA Themes 2-4 Summary ===')
for t, label in [('2', 'Cadres'), ('3', 'Couleurs'), ('4', 'Multimédia')]:
    c = counts[t]
    total = sum(c.values())
    print(f"\nTheme {t} ({label}): pass={c['pass']} fail={c['fail']} na={c['na']} total={total}")
    if fails[t]:
        print('  NC (fail):')
        for f in fails[t]:
            print(f"    - {f['test']}@{f['sample']} → {f['evidence'] or f['detail']}")
