#!/usr/bin/env python3
"""Sauvegarde preuve CDP (evidence) — pas pour scorer.

Usage: python3 scripts/audit/save-evidence.py <audit_dir> <slug> <cdp_result.json>
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def unwrap(data: dict) -> dict:
    if "result" in data and isinstance(data["result"], dict) and "value" in data["result"]:
        return data["result"]["value"]
    return data


def main() -> None:
    if len(sys.argv) < 4:
        print("Usage: save-evidence.py <audit_dir> <slug> <cdp_result.json>", file=sys.stderr)
        sys.exit(1)
    audit_dir, slug, src = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    payload = unwrap(json.loads(src.read_text(encoding="utf-8")))
    out = {
        "slug": slug,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "purpose": "evidence",
        "tools": ["browser_cdp"],
        **payload,
    }
    path = audit_dir / "samples" / f"{slug}.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"evidence saved {path}")


if __name__ == "__main__":
    main()
