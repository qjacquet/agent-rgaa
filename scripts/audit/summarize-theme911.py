#!/usr/bin/env python3
"""Summarize theme 9-11 results from audit-log.jsonl."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path


def main() -> None:
    audit_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("audits/cmvmediforce/2026-06-22")
    log = audit_dir / "audit-log.jsonl"
    stats: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    fails: list[dict] = []
    for line in log.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        e = json.loads(line)
        if e.get("event") != "test_result" or e.get("theme_id") not in ("9", "10", "11"):
            continue
        t = e["theme_id"]
        stats[t][e["agent_result"]] += 1
        if e["agent_result"] == "fail":
            fails.append({
                "theme": t,
                "test": e["test"],
                "sample": e["sample"],
                "evidence": e.get("evidence", ""),
            })
    print("=== Theme 9-11 Summary ===")
    for theme in ("9", "10", "11"):
        s = stats[theme]
        total = sum(s.values())
        print(f"Theme {theme}: pass={s['pass']} fail={s['fail']} na={s['na']} total={total}")
    print(f"\nNC (fail): {len(fails)}")
    for f in fails:
        print(f"  [{f['theme']}] {f['test']}@{f['sample']}: {f['evidence'][:100]}")


if __name__ == "__main__":
    main()
