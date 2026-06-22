#!/usr/bin/env python3
"""Merge theme 9/10/11 CDP raw responses and log audit results."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RUN = ROOT / "scripts" / "audit" / "run-theme911-only.py"


def extract(raw: dict) -> dict:
    if "exceptionDetails" in raw:
        raise SystemExit(f"CDP error: {raw['exceptionDetails']}")
    r = raw.get("result", raw)
    if isinstance(r, dict) and "value" in r:
        return r["value"]
    if "value" in raw:
        return raw["value"]
    raise SystemExit(f"No value in {list(raw.keys())}")


def main() -> None:
    if len(sys.argv) < 6:
        print(
            "Usage: merge-cdp-themes911.py <audit_dir> <sample> <url> <t9.json> <t10.json> <t11.json>",
            file=sys.stderr,
        )
        sys.exit(1)
    audit_dir, sample, url = sys.argv[1:4]
    merged: dict = {}
    for path in sys.argv[4:7]:
        merged.update(extract(json.loads(Path(path).read_text(encoding="utf-8"))))
    out = Path(f"/tmp/mcp911-{sample}.json")
    out.write_text(json.dumps({"result": {"value": merged}}, ensure_ascii=False), encoding="utf-8")
    subprocess.run([sys.executable, str(RUN), audit_dir, sample, url, str(out)], check=True)


if __name__ == "__main__":
    main()
