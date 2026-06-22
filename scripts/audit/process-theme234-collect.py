#!/usr/bin/env python3
"""Process combined theme2/3/4 CDP collect and log all results."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
AUDIT = ROOT / "scripts" / "audit"


def save_and_eval(audit_dir: Path, sample: str, url: str, theme: str, data: dict) -> None:
    ev_dir = audit_dir / "evidence"
    ev_dir.mkdir(parents=True, exist_ok=True)
    path = ev_dir / f"{sample}-theme{theme}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    subprocess.run(
        [
            sys.executable,
            str(AUDIT / f"eval-theme{theme}-batch.py"),
            str(audit_dir),
            "--sample", sample,
            "--url", url,
            "--collect", str(path),
        ],
        check=True,
    )


def main() -> None:
    audit_dir = Path(sys.argv[1])
    sample = sys.argv[2]
    url = sys.argv[3]
    raw = json.loads(sys.stdin.read())
    val = raw.get("result", {}).get("value", raw)
    if "theme2" in val:
        payload = val
    else:
        payload = {"theme2": val.get("theme2"), "theme3": val.get("theme3"), "theme4": val.get("theme4")}
    for theme in ("2", "3", "4"):
        key = f"theme{theme}"
        if payload.get(key):
            save_and_eval(audit_dir, sample, url, theme, payload[key])
    print(f"processed {sample}")


if __name__ == "__main__":
    main()
