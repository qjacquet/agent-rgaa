#!/usr/bin/env python3
"""Save repasse sample JSON from CDP result file or stdin."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

def main():
    if len(sys.argv) < 4:
        print("Usage: save-sample.py <audit_dir> <slug> <cdp_result.json>", file=sys.stderr)
        sys.exit(1)
    audit_dir = Path(sys.argv[1])
    slug = sys.argv[2]
    data = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
    # unwrap CDP result
    if "result" in data and "value" in data.get("result", {}):
        payload = data["result"]["value"]
    elif "result" in data and isinstance(data["result"], dict) and "value" in data["result"]:
        payload = data["result"]["value"]
    else:
        payload = data
    out = {
        "slug": slug,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "tools": ["browser_navigate", "Runtime.evaluate:repasse-collect.js"],
        **payload,
    }
    path = audit_dir / "samples" / f"{slug}.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    c = payload.get("collect", payload)
    print(f"saved {slug}: h1={c.get('h1Count')} linksNoText={len(c.get('linksNoText',[]))} contrastFails={payload.get('contrast',{}).get('failCount','?')}")

if __name__ == "__main__":
    main()
