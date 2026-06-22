#!/usr/bin/env python3
"""Save single combined theme5678 CDP result and log themes 5-8."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def load_value(raw: dict) -> dict:
    if "result" in raw and isinstance(raw["result"], dict) and "value" in raw["result"]:
        return raw["result"]["value"]
    if "value" in raw:
        return raw["value"]
    return raw


def main() -> None:
    if len(sys.argv) < 5:
        print("Usage: save-theme5678-from-cdp.py <audit_dir> <sample> <url> <cdp_result.json>", file=sys.stderr)
        sys.exit(1)
    audit_dir, sample, url, cdp_path = sys.argv[1:5]
    audit = Path(audit_dir)
    data = load_value(json.loads(Path(cdp_path).read_text(encoding="utf-8")))
    out = audit / "evidence" / f"{sample}-theme5678-combined.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    run = ROOT / "scripts" / "audit" / "run-theme5678-sample.py"
    subprocess.run([sys.executable, str(run), str(audit), sample, url, str(out)], check=True)
    print(f"saved+logged {sample}")


if __name__ == "__main__":
    main()
