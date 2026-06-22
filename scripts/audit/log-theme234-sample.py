#!/usr/bin/env python3
"""Log theme 2/3/4 from CDP collect dicts for one sample."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

AUDIT = Path(__file__).resolve().parents[2] / "audits/cmvmediforce/2026-06-22"
SCRIPTS = Path(__file__).resolve().parent


def log_sample(sample: str, url: str, t2: dict, t3: dict, t4: dict) -> None:
    for theme, data in [("2", t2), ("3", t3), ("4", t4)]:
        ev = AUDIT / "evidence" / f"{sample}-theme{theme}.json"
        ev.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / f"eval-theme{theme}-batch.py"),
                str(AUDIT),
                "--sample", sample,
                "--url", url,
                "--collect", str(ev),
            ],
            check=True,
        )


if __name__ == "__main__":
    sample, url = sys.argv[1], sys.argv[2]
    payload = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
    val = payload.get("result", {}).get("value", payload)
    if "theme2" in val:
        log_sample(sample, url, val["theme2"], val["theme3"], val["theme4"])
    else:
        log_sample(sample, url, val.get("t2", val), val.get("t3", val), val.get("t4", val))
