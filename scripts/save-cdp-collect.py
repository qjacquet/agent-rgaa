#!/usr/bin/env python3
"""Save CDP Runtime.evaluate result to audit sample + log."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def unwrap(data):
    if "result" in data and isinstance(data["result"], dict) and "value" in data["result"]:
        return data["result"]["value"]
    return data


def main():
    if len(sys.argv) < 4:
        print("Usage: save-cdp-collect.py <audit_dir> <slug> <cdp_result.json>", file=sys.stderr)
        sys.exit(1)
    audit_dir = Path(sys.argv[1])
    slug = sys.argv[2]
    payload = unwrap(json.loads(Path(sys.argv[3]).read_text(encoding="utf-8")))
    ts = datetime.now(timezone.utc).isoformat()
    out = {
        "slug": slug,
        "collected_at": ts,
        "tools": [
            "browser_navigate",
            "browser_snapshot",
            "Accessibility.getFullAXTree",
            "Runtime.evaluate:repasse-collect.js",
        ],
        **payload,
    }
    (audit_dir / "samples" / f"{slug}.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    log = audit_dir / "audit-log.jsonl"
    with log.open("a", encoding="utf-8") as f:
        f.write(
            json.dumps(
                {
                    "event": "sample_validate",
                    "slug": slug,
                    "url": payload.get("collect", {}).get("url", ""),
                    "http": 200,
                    "status": "ok",
                    "timestamp": ts,
                },
                ensure_ascii=False,
            )
            + "\n"
        )
        f.write(
            json.dumps(
                {
                    "event": "cdp_collect",
                    "sample": slug,
                    "tools": ["snapshot", "axtree", "collect", "contrast"],
                    "timestamp": ts,
                },
                ensure_ascii=False,
            )
            + "\n"
        )
    c = payload.get("collect", {})
    print(
        f"OK {slug}: h1={c.get('h1Count')} linksNoText={len(c.get('linksNoText', []))} "
        f"contrastFails={payload.get('contrast', {}).get('failCount')}"
    )


if __name__ == "__main__":
    main()
