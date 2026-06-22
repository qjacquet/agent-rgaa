#!/usr/bin/env python3
"""Merge theme56 + theme78 CDP MCP results, save combined collect, log themes 5-8."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def load_value(path: Path) -> dict:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if "result" in raw and isinstance(raw["result"], dict) and "value" in raw["result"]:
        return raw["result"]["value"]
    if "value" in raw:
        return raw["value"]
    return raw


def main() -> None:
    if len(sys.argv) < 6:
        print("Usage: merge-theme5678-cdp-results.py <audit_dir> <sample> <url> <theme56.json> <theme78.json>", file=sys.stderr)
        sys.exit(1)
    audit_dir, sample, url, p56, p78 = sys.argv[1:6]
    audit = Path(audit_dir)
    t56 = load_value(Path(p56))
    t78 = load_value(Path(p78))
    combined = {**t56, **{k: v for k, v in t78.items() if k != "url"}, "url": t78.get("url") or t56.get("url")}
    out = audit / "evidence" / f"{sample}-theme5678-combined.json"
    out.write_text(json.dumps(combined, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    run = ROOT / "scripts" / "audit" / "run-theme5678-sample.py"
    subprocess.run([sys.executable, str(run), str(audit), sample, url, str(out)], check=True)
    print(f"merged+logged {sample}")


if __name__ == "__main__":
    main()
