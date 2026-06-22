#!/usr/bin/env python3
"""Process theme2/3/4 CDP collect files for one sample and log results."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
AUDIT_SCRIPTS = ROOT / "scripts" / "audit"


def unwrap(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "result" in data and isinstance(data["result"], dict) and "value" in data["result"]:
        val = data["result"]["value"]
        if isinstance(val, dict) and "theme2" in val:
            return val
        return {"theme2": val} if path.name.startswith("theme2") else val
    return data


def save_eval(audit_dir: Path, sample: str, url: str, theme: str, data: dict) -> None:
    ev = audit_dir / "evidence" / f"{sample}-theme{theme}.json"
    ev.parent.mkdir(parents=True, exist_ok=True)
    ev.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    subprocess.run(
        [
            sys.executable,
            str(AUDIT_SCRIPTS / f"eval-theme{theme}-batch.py"),
            str(audit_dir),
            "--sample", sample,
            "--url", url,
            "--collect", str(ev),
        ],
        check=True,
    )


def main() -> None:
    audit_dir, sample, url = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
    base = Path(sys.argv[4])
    payload = {}
    if base.is_file():
        payload = unwrap(base)
    else:
        for theme in ("2", "3", "4"):
            p = base / f"theme{theme}.json"
            if p.exists():
                payload[f"theme{theme}"] = unwrap(p)
    for theme in ("2", "3", "4"):
        key = f"theme{theme}"
        if key in payload and payload[key]:
            save_eval(audit_dir, sample, url, theme, payload[key])
    print(f"logged themes 2-4 for {sample}")


if __name__ == "__main__":
    main()
