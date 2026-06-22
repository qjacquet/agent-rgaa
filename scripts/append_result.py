#!/usr/bin/env python3
"""Merge CDP results into samples/*.json — usage: append_result.py <slug> <cdp_json_file>"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

AUDIT = Path(__file__).resolve().parent.parent / "audits/cmvmediforce-fr/2026-06-22"

def main():
    slug, fpath = sys.argv[1], Path(sys.argv[2])
    raw = json.loads(fpath.read_text(encoding="utf-8"))
    val = raw.get("result", {}).get("value", raw)
    out = {
        "slug": slug,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "tools": ["browser_navigate", "Runtime.evaluate:repasse-collect.js"],
        **val,
    }
    (AUDIT / "samples" / f"{slug}.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (AUDIT / "audit-log.jsonl").open("a", encoding="utf-8") as log:
        log.write(json.dumps({"event": "cdp_collect", "sample": slug, "tools": ["collect", "contrast", "meta"]}, ensure_ascii=False) + "\n")
    c = val.get("collect", {})
    print(f"OK {slug} h1={c.get('h1Count')} contrastFails={val.get('contrast', {}).get('failCount')}")

if __name__ == "__main__":
    main()
